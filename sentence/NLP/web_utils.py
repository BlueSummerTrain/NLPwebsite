#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import re
import codecs
import config as cf
import numpy as np
import web_mode_config as webconfig
from ner_helpers import response2device
#########web models used code here########
def time_str_replace(sentence):
    hour = u'\u70b9'
    mint = u'\u5206'
    seconds = u'\u79d2'
    line_res = ''
    line = sentence.split(':')
    if len(line) == 3:
        line_res = line[0] + hour + line[1] + mint + line[2] + seconds
    elif len(line) == 2:
        line_res = line[0] + hour + line[1] + mint
    return line_res

def get_time_str(sentence):
    tmp_seq = sentence
    time_strs_1 = re.findall(r'[0-9]{0,4}:[0-9]{0,4}:[0-9]{0,4}',tmp_seq)
    for item in time_strs_1:
        tmp_seq = tmp_seq.replace(item,'')
    time_strs_2 = re.findall(r'[0-9]{0,4}:[0-9]{0,4}',tmp_seq)
    time_strs = time_strs_1 + time_strs_2
    for it_time in time_strs:
        it_time_new = time_str_replace(it_time)
        sentence = sentence.replace(it_time,it_time_new)
    return sentence
'''
delete comma in sentence
'''
def delete_comma(sentence):
    sentence = sentence.decode('utf-8').strip()
    sentence = sentence.replace(" ", "_")
    
    if sentence.startswith(u'\u5c0ft'):
        sentence = sentence.replace(u'\u5c0ft', "")

    if ':' in sentence:
        sentence = get_time_str(sentence)

    sentence = re.sub(ur"[^\u4e00-\u9fffA-Za-z0-9\u1573\u1402\u1405\u1401\u15d1\._\/\-+×÷]","",sentence)

    if u'\u15d1' in sentence:
        sentence = sentence.replace(u'\u15d1', u'\u1401')

    sentence = sentence.lower()
    return sentence.encode('utf-8')

'''
nmt command replace here
'''
def nmt_replace_dict(config_path):
    dict_res = {}
    with open(config_path,'r') as nmt_r:
        nmt_cmds = nmt_r.read().strip().decode('utf-8').split('\n')
	for cmd in nmt_cmds:
		if '#' not in cmd[0]:
			cmd_t = cmd.split('/')
			dict_res[cmd_t[0]] = cmd_t[0] +'/'+ cmd_t[-1]
	return dict_res
def nmt_cmd_replace(nmt,ner_res,nmt_dict):

    if nmt in nmt_dict.keys():
        nmt_cmd = nmt_dict[nmt]
        if '/' in nmt_cmd or ']/' in nmt_cmd:
            if '/' in nmt_cmd:
                spt = '/'
            if ']/' in nmt_cmd:
                spt = ']/'
            nmt_cmd_n = nmt_cmd.split(spt)
            nmt_cmd_res = response2device(nmt_cmd_n[0],ner_res)
            nmt_cmd = nmt_cmd_res + spt + nmt_cmd_n[-1]
        else:
            nmt_cmd = response2device(nmt_cmd,ner_res)
    else:
        nmt_cmd = response2device(nmt,ner_res)
    return nmt_cmd

if __name__ == '__main__':
    print nmt_cmd_replace('+ degree','conf/home.command.conf').encode('utf-8')
