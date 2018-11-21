# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import os
import sys
import threading
from datetime import datetime

import bson
import mongoengine

import NLP.config as cf
import NLP.web_mode_config as webconfig
from NLP.mode_and_replace import mode_and_replace
from NLP.ner_helpers import mergeMainObj
from NLP.nlp_num import ch_num_en_num_recognize
from NLP.nlp_web_module import NMTServerModel, \
    NERServerModel, \
    SceneCLS, \
    TextClassifyWebModel, \
    Namecls, \
    SceneCLSCNN, \
    CHATServerModel
from NLP.web_utils import delete_comma, nmt_cmd_replace, nmt_replace_dict

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')


class nlpdatastore(mongoengine.Document):
    Error_data = mongoengine.BinaryField(max_bytes=1024000)
    Data_flag = mongoengine.StringField(max_length=10)
    date = mongoengine.DateTimeField(default=datetime.now(), required=True)


class database():

    def insert_db(self, db_data, data_flag):
        bson_data = bson.BSON.encode(db_data)
        nlpdatastore.objects.create(Error_data=bson_data, Data_flag=data_flag)

    def query_db(self, data_flag_check):
        query_data = []
        queryset = nlpdatastore.objects.filter(Data_flag=data_flag_check)
        for item in queryset:
            re_data = item.Error_data
            re_data = bson.BSON(re_data)  # bson.binary.Binary to bson.BSON
            ecoded_doc = bson.BSON.decode(re_data)
            ecoded_doc = json.dumps(ecoded_doc, ensure_ascii=False)
            query_data.append(ecoded_doc)
        return query_data

    def delete_data(self, data_flag_delete):
        queryset = nlpdatastore.objects.filter(
            Data_flag=data_flag_delete).delete()


class BaseModel(object):

    def __init__(self):
        if webconfig.CONFIG_MODE == webconfig.TV_MODE:
            path = os.getcwd() + '/sentence/NLP/models/tv/'
            self.scenecls_model = SceneCLS(path)

        if webconfig.CONFIG_MODE == webconfig.PHONE_MODE:
            path = os.getcwd() + '/sentence/NLP/models/phone/'
            self.cls_phone = TextClassifyWebModel(path)
            self.cls_name_phone = Namecls(path)

        if webconfig.CONFIG_MODE == webconfig.NTV_MODE:
            path = os.getcwd() + '/sentence/NLP/models/newtv/'
            self.scenecls_model = SceneCLSCNN(path)

        if webconfig.CONFIG_MODE == webconfig.NGTV_MODE:
            path = os.getcwd() + '/sentence/NLP/models/ngtv/'
            self.scenecls_model = SceneCLS(path)

        if webconfig.CONFIG_MODE == webconfig.CHAT_MODE:
            path = os.getcwd() + '/sentence/NLP/models/chat/'
            self.chat_server_model = CHATServerModel(path)
            # no nessesary to load NER and NMT model.
            return

        # if webconfig.CONFIG_MODE == webconfig.HOME_MODE:
        #    path = os.getcwd() + '/sentence/NLP/models/home/'
        #    self.scenecls_model = SceneCLS(path)

        self.nmt_server_model = NMTServerModel(path)
        self.NER_server_model = NERServerModel(path, 'main')
        self.NER_server_model_obj = NERServerModel(path, 'obj')


class NLPThread(threading.Thread):

    def __init__(self, func, arg):
        threading.Thread.__init__(self)
        self.func = func
        self.arg = arg
        self.result = self.func(self.arg)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


class NlpScene(BaseModel):
    """docstring for Scene"""

    def __init__(self):
        super(NlpScene, self).__init__()
        pass

    def __call__(self, parse_word):
        process_res = self.scenecls_model(parse_word)
        # process_res = {'scene': process_res, 'version': webconfig.version}
        return process_res


class NLPHandler(BaseModel):

    def __init__(self):
        super(NLPHandler, self).__init__()
        if webconfig.CONFIG_MODE != webconfig.CHAT_MODE:
            self.nmt_dict = nmt_replace_dict(webconfig.CONFIG_PATH)
            self.scene_cls = NlpScene()

    def check_data(self, data_input):
        if (webconfig.CONFIG_MODE == webconfig.CHAT_MODE):
            return data_input
        data_input = delete_comma(data_input)
        data_input = data_input.strip()
        data_input = data_input.decode('utf-8')
        return data_input

    def get_ner_info(self, parse_word):
        return self.NER_server_model(parse_word)

    def get_ner_obj_info(self, nmt_data):
        return self.NER_server_model_obj(nmt_data)

    def merge_main_obj(self, main_ner, obj_location):
        if len(obj_location) > 0:
            res = mergeMainObj(main_ner, obj_location)
        else:
            res = main_ner
        return res

    def __call__(self, data_in, task):
        data_res = {}
        parse_word = self.check_data(data_in)
        logger.info(parse_word)
        # data res
        ner_res = None
        nmt_res = None
        cf_res = None
        scene_res = None
        final = None
        cls_seq = ''

        if parse_word == '':
            return data_res
        if task == 'scene':
            data_res = self.scene_cls(parse_word)
        elif task == 'ner':
            main_ner, nmt_data, cls_seq = self.get_ner_info(parse_word)
            obj_location = self.get_ner_obj_info(nmt_data)
            if obj_location != None:
                res = self.merge_main_obj(main_ner, obj_location)
            else:
                res = main_ner
            data_res = {'ner': res}
        elif task == 'nmt':
            res = self.nmt_server_model(parse_word)
            res = mode_and_replace(
                mmode='all', smode='all', sentence=res, mode=2)
            data_res = {'nmt': res}
        elif task == 'chat':
            res = self.chat_server_model(parse_word)
            data_res = res
        else:
            t_start = datetime.now()
            number_data = ch_num_en_num_recognize(parse_word)
            if number_data != 'NULL':
                ner_res = [{'NUM': parse_word}]
                nmt_data = cf.NUM
            else:
                main_ner, nmt_data, cls_seq = self.get_ner_info(parse_word)
                obj_location = self.get_ner_obj_info(nmt_data)
                if obj_location != None:
                    ner_res = self.merge_main_obj(main_ner, obj_location)
                else:
                    ner_res = main_ner
            if webconfig.CONFIG_MODE == webconfig.PHONE_MODE:
                cf_res = self.cls_phone(nmt_data)
                if '0' in cf_res:
                    return {'textcf': '0'},'NULL'
                # phone name text classify here
                names = []
                for data in ner_res:
                    key_name = data.keys()[0]
                    if key_name == 'NAME' or key_name == 'NAME_obj':
                        if data[key_name] not in names:
                            names.append(data[key_name])
                cls_names = self.cls_name_phone(names)

            if webconfig.CONFIG_MODE == webconfig.NTV_MODE:
                print "scene data:", cls_seq
                scene_res = self.scene_cls(cls_seq)
            if webconfig.CONFIG_MODE == webconfig.PHONE_MODE:
                nmt_res = self.nmt_server_model(cls_seq)
            else:
                nmt_res = self.nmt_server_model(nmt_data)
            nmt_res = mode_and_replace(mmode='all', smode='all', sentence=nmt_res, mode=2)
            final = nmt_cmd_replace(nmt_res, ner_res, self.nmt_dict)

            data_res = {'ner': ner_res, 'nmt': nmt_res, 'scene': scene_res,
                        'final': final, 'version': webconfig.version}
            if webconfig.CONFIG_MODE == webconfig.PHONE_MODE:
                data_res = {'textcf': cf_res, 'name_cls': cls_names, 'ner': ner_res,
                            'nmt': nmt_res, 'final': final, 'version': webconfig.version}
                # data_res = {'textcf': cf_res, 'ner': ner_res,'nmt': nmt_res, 'final': final, 'version': webconfig.version}
            all_t_end = datetime.now()
            print "ALL cost:", (all_t_end - t_start).total_seconds(), 'seconds'
        return data_res, cls_seq
