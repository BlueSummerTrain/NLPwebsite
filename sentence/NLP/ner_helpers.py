#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import config as cf
import numpy as np
import codecs
import re
import collections
import copy
'''
extract name entity of one sentence
'''
def extractNameEntity(label,sentence):
    name_content = []
    name_key = ''
    namelist = []
    entity_locs = []
    entity_indx = 0
    label = label.split(' ')
    for index,keylabel in enumerate(label):
        if index >= len(sentence):
            break
        if sentence[index] == '_':
            sentence[index] = ' '
        if keylabel!='O':
            keylabel = keylabel.split('_')
            if keylabel[0] == 'S':
                entity_indx = index
                name_key = keylabel[1]
                name_content.append(sentence[index])
                key_content = ''.join(name_content)
                namedict = {name_key:key_content}
                namelist.append(namedict)
                entity_locs.append(entity_indx)
                name_content = []
                continue
            if keylabel[0] == 'B':
                entity_indx = index
                name_key = keylabel[1]
                name_content.append(sentence[index])
            if keylabel[0]== 'I':
                name_key = keylabel[1]
                name_content.append(sentence[index])
            if keylabel[0] == 'E':
                name_key = keylabel[1]
                name_content.append(sentence[index])
                key_content = ''.join(name_content)
                namedict = {name_key:key_content}
                namelist.append(namedict)
                entity_locs.append(entity_indx)
                name_content = []
    return namelist,entity_locs

def transform2NMTstyle(data_result,ner_locs,sentences):
    sentence = ''.join(sentences[0])
    sentence_cls = copy.deepcopy(sentence)
    sort_data = []
    for data in data_result:
        sort_data.append(data.items()[0])
    for index,data in enumerate(sort_data):
        key,value = data
        vlen = len(value)
        pos = 0
        while pos >= 0:
            pos = sentence.find(value,pos)
            '''
            reach the end pos
            '''
            if pos < 0:
                break
            '''
            find the next pos,need subtract the last entity len and add 1
            '''
            current_pos = ner_locs[index]
            if index > 0:
                for i in range(index):
                    current_pos = current_pos - len(sort_data[i][1]) + 1
            '''
            replace entity here
            '''
            if pos == current_pos:
                head_seq = sentence[:pos]
                tail_seq = sentence[pos + vlen:]
                head = sentence_cls[:pos]
                tail = sentence_cls[pos + vlen:]
                sentence = head_seq + cf.trans_tag_dict[key] + tail_seq
                sentence_cls = head + cf.trans_tag_dict_scene[key] + tail
                break
            else:
                pos = pos + 1
    return sentence,sentence_cls

def ner_return(ner_list):
    ner_res = collections.OrderedDict()
    for item in ner_list:
        key,value = item.items()[0]
        if ner_res.has_key(value):
            continue
        else:
            ner_res[value] = key
    return ner_res
'''
find object location
'''
def findObjectLocation(labels_seq,sentence):
    index_obj = []
    i_obj = 0
    labels_seq = labels_seq.split(' ')
    try:
        for index,item in enumerate(sentence):
            if item in [cf.NAME,cf.NUM,cf.TI,cf.TV_CH]:
                i_obj = i_obj + 1
                if labels_seq[index] == 'O':
                    pass
                elif labels_seq[index] == 'S_OBJ':
                    index_obj.append(i_obj-1)
    except Exception, e:
        print "wrong obj label!"
        return None
    return index_obj

'''
split ner seq data to list
'''
def split_sentences(lines):
    all_line = []
    for line in lines:
        line = line.decode('utf-8')
        line = ''.join([word + '\t' for word in line])
        line=line.split('\t')
        line.remove('')
        if u'\u3002' in line:
            line.remove(u'\u3002')
        if u'\n' in line:
            line.remove(u'\n')
        all_line.append(line)
    return all_line

def ner_convert_to_ids_by_single(sentence,src_datas_vocab):
    if (sentence == None or sentence == ''):
        return None
    seq = []
    seq_len = []
    sentence = sentence[:cf.NER_INPUT_LEN]
    for word in sentence:
        d_id = 0
        if (src_datas_vocab.has_key(word)):
            d_id = src_datas_vocab[word]
        seq.append(d_id)

    seq += [cf.NMT_EOS_ID] + [cf.PADDING]
    seq = np.array(seq, dtype=np.int32)
    seq = seq.reshape(1, -1)
    return seq

def get_batch_string_by_index(rnn_output,tgt_datas_rev_vocab):
    data_out = []
    if (tgt_datas_rev_vocab == None):
        return data_out
    output_len = len(rnn_output)
    for i in range(output_len):
        out = rnn_output[i]
        res_str_list = []
        out = out[:-1]
        for j in range(len(out)):
            t = tgt_datas_rev_vocab[out[j]]
            if (t != u'</s>' and t != u'<padding>'):
                if t == u'<unk>':
                    t = ''
                res_str_list.append(t)
            else:
                break
        data_out.append(' '.join(res_str_list))
    return data_out

def init_ner_vocab(src_vocab_file, tgt_vocab_file):
    # init the vocab from vocab_corpus
    src_datas_vocab = {}
    tgt_datas_vocab = {}
    tgt_datas_rev_vocab = {}

    if (src_vocab_file != ''):
        with codecs.open(src_vocab_file, 'r', encoding='utf-8') as src_f:
            src_vocab_lines = src_f.readlines()
            src_temp_vocab = {}
            for line in src_vocab_lines:
                line = line.strip()
                if (line.endswith(u'\n')):
                    line = line[:-1]
                src_temp_vocab[line] = len(src_temp_vocab)
            src_datas_vocab = src_temp_vocab
            del src_temp_vocab

    if(tgt_vocab_file != ''):
        with codecs.open(tgt_vocab_file, 'r', encoding='utf-8') as tgt_f:
            tgt_vocab_lines = tgt_f.readlines()
            tgt_temp_vocab = {}
            for line in tgt_vocab_lines:
                line = line.strip()
                if (line.endswith(u'\n')):
                    line = line[:-1]
                tgt_temp_vocab[line] = len(tgt_temp_vocab)
            tgt_datas_vocab = tgt_temp_vocab
            del tgt_temp_vocab

            temp_rev_vocab = {}
            for (i, j) in zip(tgt_datas_vocab.keys(), tgt_datas_vocab.values()):
                temp_rev_vocab[j] = i
            tgt_datas_rev_vocab = temp_rev_vocab
    return src_datas_vocab,tgt_datas_vocab,tgt_datas_rev_vocab

def mergeMainObj(main_ner,obj_location):
    for i_location in obj_location:
        # check for safe
        try:
            obj_entity = main_ner[i_location]
        except IndexError, e:
            print(e)
            break;
        for item in main_ner:
            key = item.keys()[0]
            if obj_entity.has_key(key):
                if obj_entity[key] == item[key]:
                    new_key = key
                    if not new_key.endswith('_obj'):
                        new_key = key + '_obj'
                    new_item = {new_key:obj_entity[key]}
                    '''
                    replace item in main_ner
                    '''
                    main_ner[main_ner.index(item)] = new_item
    return main_ner

def response2device(nmt_res,ner_list):
    names_label_list = cf.Name_labels
    mutil_names = []
    #contact mutil words
    for item in cf.mutil_words:
        if item in nmt_res:
            item_sub = item.replace(' ','-')
            mutil_names.append(item_sub)
            nmt_res = nmt_res.replace(item,item_sub)
    #delete ( )
    if len(mutil_names) > 0:
        nmt_res_list = nmt_res.split(' ')
        for index,nmt_item in enumerate(nmt_res_list):
            if nmt_item in mutil_names:
                if index -1 > 0 and index + 1 < len(nmt_res_list):
                    if nmt_res_list[index -1] == '(' and nmt_res_list[index +1] == ')':
                        nmt_res_list.pop(index -1)
                        nmt_res_list.pop(index)
        nmt_res = ' '.join(nmt_res_list)
    names_label_list = names_label_list + mutil_names
    #resort ner entity for entity replace
    ner_res = {}
    for item in ner_list:
        key = item.keys()[0]
        if ner_res.has_key(key):
            ner_res[key].append(item[key])
        else:
            ner_res[key] = [item[key]]

    def find_pos_str(nmt_res,pos):
        pos = nmt_res.find('$',pos)
        if pos < 0:
            return 'NULL',-1
        label_pos = nmt_res.find(' ',pos)
        if label_pos < 0:
            label_str = nmt_res[pos:]
        else:
            label_str = nmt_res[pos:label_pos]
        return label_str,pos
    def replace_function(nmt_res,label_list,content):
        i = 0
        pos = 0
        while (i < len(content)):
            replaced = False
            label_str,pos = find_pos_str(nmt_res,pos)
            if label_str == 'NULL' or pos < 0:
                break
            if label_str in label_list:
                nmt_res = nmt_res.replace(label_str,content[i],1)
                replaced = True
            if pos >= 0:
                pos = pos + 1
            else:
                break
            if replaced:
                i = i + 1

        return nmt_res
    try:
        if 'NAME_obj' in ner_res.keys():
            nmt_res = replace_function(nmt_res,names_label_list,ner_res['NAME_obj'])
        if 'APP_obj' in ner_res.keys():
            nmt_res = replace_function(nmt_res,names_label_list,ner_res['APP_obj'])
        if 'PER_obj' in ner_res.keys():
            nmt_res = replace_function(nmt_res,names_label_list,ner_res['PER_obj'])
        if 'LOC_obj' in ner_res.keys():
            nmt_res = replace_function(nmt_res,names_label_list,ner_res['LOC_obj'])
        if 'GOODS_obj' in ner_res.keys():
            nmt_res = replace_function(nmt_res,names_label_list,ner_res['GOODS_obj'])
        if 'MEDIA_obj' in ner_res.keys():
            nmt_res = replace_function(nmt_res,names_label_list,ner_res['MEDIA_obj'])
        if 'ORG_obj' in ner_res.keys():
            nmt_res = replace_function(nmt_res,names_label_list,ner_res['ORG_obj'])
        if 'NUM_obj' in ner_res.keys():
            nmt_res = replace_function(nmt_res,cf.Num_labels,ner_res['NUM_obj'])
        if 'TI_obj' in ner_res.keys():
            nmt_res = replace_function(nmt_res,cf.Ti_labels,ner_res['TI_obj'])
        if 'ATV_obj' in ner_res.keys():
            nmt_res = replace_function(nmt_res,cf.atv_labels,ner_res['ATV_obj'])
        if 'NAME' in ner_res.keys():
            nmt_res = replace_function(nmt_res,names_label_list,ner_res['NAME'])
        if 'APP' in ner_res.keys():
            nmt_res = replace_function(nmt_res,names_label_list,ner_res['APP'])
        if 'PER' in ner_res.keys():
            nmt_res = replace_function(nmt_res,names_label_list,ner_res['PER'])
        if 'LOC' in ner_res.keys():
            nmt_res = replace_function(nmt_res,names_label_list,ner_res['LOC'])
        if 'GOODS' in ner_res.keys():
            nmt_res = replace_function(nmt_res,names_label_list,ner_res['GOODS'])
        if 'MEDIA' in ner_res.keys():
            nmt_res = replace_function(nmt_res,names_label_list,ner_res['MEDIA'])
        if 'ORG' in ner_res.keys():
            nmt_res = replace_function(nmt_res,names_label_list,ner_res['ORG'])
        if 'NUM' in ner_res.keys():
            nmt_res = replace_function(nmt_res,cf.Num_labels,ner_res['NUM'])
        if 'TI' in ner_res.keys():
            nmt_res = replace_function(nmt_res,cf.Ti_labels,ner_res['TI'])
        if 'ATV' in ner_res.keys():
            nmt_res = replace_function(nmt_res,cf.atv_labels,ner_res['ATV'])
        if len(ner_res.keys()) == 0:
            nmt_res = replace_function(nmt_res,names_label_list,cf.NAME)
    except Exception, e:
        return 'NLP inner errors!'   
    return nmt_res