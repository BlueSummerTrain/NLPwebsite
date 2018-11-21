#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import tensorflow as tf
import numpy as np
import sys
import math
import config as cf
from datetime import datetime
import ner_helpers as ner_h
import nmt_helpers as nmt_h
import cls_scene_helpers as cls_scene_h
import cls_helpers as cls_h

################################################


def get_tensor_graph(model_pb_file):
    with tf.gfile.GFile(model_pb_file, "rb") as f:
        graph_o = tf.GraphDef()
        graph_o.ParseFromString(f.read())
    with tf.Graph().as_default() as G:
        tf.import_graph_def(graph_o,
                            input_map=None,
                            return_elements=None,
                            name='',
                            op_dict=None,
                            producer_op_list=None)
    return G

class TextClassifyWebModel(object):
    def __init__(self,path):
        self.graph = get_tensor_graph(path+cf.CF_FROZEN_MODEL)
        self.text_input = self.graph.get_tensor_by_name(cf.CF_INPUT_NODE_1)
        self.result = self.graph.get_tensor_by_name(cf.CF_OUTPUT_NODE_1)
        self.voc,_ = cls_h.read_vocabulary(path+cf.CF_VOC_PATH)
        self.sess = tf.Session(graph=self.graph)

    def __call__(self,str_data):
        cf_t_start = datetime.now()
        data_input = [str_data]
        resultdata = []
        x_data = cls_h.read_data_from_strs(data_input,32)
        x_test = np.array(cls_h.sentence2matrix(x_data,32,self.voc))
        get_batches = cls_h.batch_iter(list(x_test), 1, 1, shuffle=False)
        for x_test_batch in get_batches:
            batch_predictions = self.sess.run(self.result, {self.text_input: x_test_batch})
            predict_datas = batch_predictions.tolist()
            for predict_data in predict_datas:
                resultdata.append(predict_data.index(max(predict_data)))
        cf_t_end = datetime.now()
        print "TCT CLS cost:",(cf_t_end - cf_t_start).total_seconds(),'seconds'
        return str(resultdata[0])

class SceneCLS(object):

    def __init__(self, path):
        self.graph = get_tensor_graph(path + cf.SCENE_PATH)
        self.scene_input = self.graph.get_tensor_by_name(cf.SCENE_INPUT_NODE)
        self.result = self.graph.get_tensor_by_name(cf.SCENE_OUTPUT_NODE)
        self.voc = cls_scene_h.read_vocabulary(path + cf.SCENE_VOCAB_PATH)
        self.sess = tf.Session(graph=self.graph)

    def __call__(self, scene_data):
        name_t_start = datetime.now()
        batches = cls_scene_h.get_batch_data(scene_data, self.voc,cf.SCENE_MAX_LENGTH)
        res = []
        for x_test_batch in batches:
            batch_predictions = self.sess.run(self.result, {self.scene_input: x_test_batch})
            res.extend(batch_predictions.tolist())
        res_f = []
        for item in res:
            res_f.append(cls_scene_h.translate_readable_logit(item, 3))
        name_t_end = datetime.now()
        print "SceneCLS cost:", (name_t_end - name_t_start).total_seconds(), 'seconds'
        return res_f[0]

class SceneCLSCNN(object):
    def __init__(self, path):
        self.graph = get_tensor_graph(path + cf.SCENECNN_PATH)
        self.scenecnn_input0 = self.graph.get_tensor_by_name(cf.SCENECNN_INPUT_NODE0)
        self.scenecnn_input1 = self.graph.get_tensor_by_name(cf.SCENECNN_INPUT_NODE1)
        self.resultcnn = self.graph.get_tensor_by_name(cf.SCENECNN_OUTPUT_NODE)
        self.voc = cls_scene_h.read_vocabulary(path + cf.SCENECNN_VOCAB_PATH)
        self.sess = tf.Session(graph=self.graph)

    def __call__(self, scene_data):
        name_t_start = datetime.now()
        batches = cls_scene_h.get_batch_data(scene_data, self.voc,cf.SCENECNN_MAX_LENGTH)
        res = []
        for x_test_batch in batches:
            batch_predictions = self.sess.run(self.resultcnn, {self.scenecnn_input0: x_test_batch,self.scenecnn_input1:1.0})
            res.extend(batch_predictions.tolist())
        res_f = []
        for item in res:
            res_f.append(cls_scene_h.translate_readable_logit(item, 3))
        name_t_end = datetime.now()
        print "SceneCLSCNN cost:", (name_t_end - name_t_start).total_seconds(), 'seconds'
        return res_f[0]

class Namecls(object):
    """name cls for tct phone"""
    def __init__(self, path):
        self.graph = get_tensor_graph(path + cf.TCTNAME_PATH)
        self.tctname_input = self.graph.get_tensor_by_name(cf.TCTNAME_INPUT_NODE)
        self.tctname_result = self.graph.get_tensor_by_name(cf.TCTNAME_OUTPUT_NODE)
        self.voc = cls_scene_h.read_vocabulary(path + cf.TCTNAME_VOCAB_PATH)
        self.sess = tf.Session(graph=self.graph)
    def __call__(self,data_name):
        name_t_start = datetime.now()
        batches = cls_scene_h.get_batch_data(data_name, self.voc,cf.TCTNAME_MAX_LENGTH)
        res = []
        for x_test_batch in batches:
            batch_predictions = self.sess.run(self.tctname_result, {self.tctname_input: x_test_batch})
            res = res + batch_predictions.tolist()
        res_dict = {}
        for inx,data_item in enumerate(res):
            res_max_inx = data_item.index(max(data_item))
            res_dict[data_name[inx]]=cf.NAME_DICT[res_max_inx]
        name_t_end = datetime.now()
        print "TCT NAMECLS cost:",(name_t_end - name_t_start).total_seconds(),'seconds'
        return res_dict

class NERServerModel(object):

    def __init__(self, path, flag):
        self.flag = flag
        if flag == 'main':
            self.NER_FROZEN_MODEL = 'ner/main/ner.pb'
            self.NER_VOC_DATA = 'ner/main/vocab.na.data'
            self.NER_VOC_LABEL = 'ner/main/vocab.lf.data'
        elif flag == 'obj':
            self.NER_FROZEN_MODEL = 'ner/obj/ner_obj.pb'
            self.NER_VOC_DATA = 'ner/obj/vocab.na.data'
            self.NER_VOC_LABEL = 'ner/obj/vocab.lf.data'

        self.graph = get_tensor_graph(path + self.NER_FROZEN_MODEL)
        self.sess = tf.Session(graph=self.graph)
        self.x1 = self.sess.graph.get_tensor_by_name(cf.NER_INPUT_NODE_1)
        self.y = self.sess.graph.get_tensor_by_name(cf.NER_OUTPUT_NODE_1)
        self.src_datas_vocab, self.tgt_datas_vocab, self.tgt_datas_rev_vocab = \
            ner_h.init_ner_vocab(path + self.NER_VOC_DATA,
                                 path + self.NER_VOC_LABEL)

    def __call__(self, sentence):
        t_start = datetime.now()
        sen = ner_h.ner_convert_to_ids_by_single(
            sentence, self.src_datas_vocab)
        res_arr = self.sess.run(self.y, feed_dict={self.x1: sen})
        res = ner_h.get_batch_string_by_index(res_arr, self.tgt_datas_rev_vocab)
        seq = ner_h.split_sentences([sentence])
        if self.flag == 'main':
            ner_info,ner_locs = ner_h.extractNameEntity(res[0], seq[0])
            nmt_sentence,cls_sentence = ner_h.transform2NMTstyle(ner_info, ner_locs, seq)
            t_end = datetime.now()
            print "NER cost:", (t_end - t_start).total_seconds(), 'seconds'
            return ner_info, nmt_sentence,cls_sentence
        else:
            ner_obj_location = ner_h.findObjectLocation(res[0], seq[0])
            t_end = datetime.now()
            print "NER_OBJ cost:", (t_end - t_start).total_seconds(), 'seconds'
            return ner_obj_location


class NMTServerModel(object):

    def __init__(self, path):
        self.graph = get_tensor_graph(path + cf.NMT_FROZEN_MODEL)
        self.sess = tf.Session(graph=self.graph)
        self.x1 = self.sess.graph.get_tensor_by_name(cf.NMT_INPUT_NODE_1)
        self.x2 = self.sess.graph.get_tensor_by_name(cf.NMT_INPUT_NODE_2)
        self.y = self.sess.graph.get_tensor_by_name(cf.NMT_OUTPUT_NODE_1)
        self.src_datas_vocab, self.tgt_datas_vocab, self.tgt_datas_rev_vocab = \
            nmt_h.init_nmt_vocab(path + cf.DATA_VOCAB_FILE,
                                 path + cf.LABEL_VOCAB_FILE)

    def __call__(self, sentence):
        nmt_t_start = datetime.now()
        sen, slen = nmt_h.nmt_convert_to_ids_by_single(
            sentence, self.src_datas_vocab)
        res_arr = self.sess.run(
            self.y, feed_dict={self.x1: sen, self.x2: slen})
        res = nmt_h.nmt_get_string_by_index(res_arr, self.tgt_datas_rev_vocab)
        nmt_t_end = datetime.now()
        print "NMT cost:", (nmt_t_end - nmt_t_start).total_seconds(), 'seconds'

        return res


# NOTE: for chat model, we use many functions from NMT module.
class CHATServerModel(object):

    def __init__(self, path):
        self.graph = get_tensor_graph(path + cf.CHAT_FROZEN_MODEL)
        self.sess = tf.Session(graph=self.graph)
        self.x1 = self.sess.graph.get_tensor_by_name(cf.CHAT_INPUT_NODE_1)
        self.x2 = self.sess.graph.get_tensor_by_name(cf.CHAT_INPUT_NODE_2)
        self.y = self.sess.graph.get_tensor_by_name(cf.CHAT_OUTPUT_NODE_1)
        self.src_datas_vocab, self.tgt_datas_vocab, self.tgt_datas_rev_vocab = \
            nmt_h.init_nmt_vocab(path + cf.CHAT_NA_VOCAB_FILE,
                                 path + cf.CHAT_LF_VOCAB_FILE)

    def __call__(self, sentence):
        nmt_t_start = datetime.now()
        sen, slen = nmt_h.nmt_convert_to_ids_by_single(
            sentence, self.src_datas_vocab)
        res_arr = self.sess.run(
            self.y, feed_dict={self.x1: sen, self.x2: slen})
        res = nmt_h.nmt_get_string_by_index(res_arr, self.tgt_datas_rev_vocab)
        nmt_t_end = datetime.now()
        print "CHAT cost:", (nmt_t_end - nmt_t_start).total_seconds(), 'seconds'
        res = res.replace(' ', '')
        return res

if __name__ == '__main__':
    pass
