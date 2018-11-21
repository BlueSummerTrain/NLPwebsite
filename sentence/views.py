# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,HttpResponse
from django.http import HttpResponseRedirect
from models import database,NLPHandler,NlpScene
import json
import copy
import logging
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

db_data ={} 
db = database()
nlp = NLPHandler()
scene = NlpScene()

def get_web_data(request,label):
	if request.method == 'GET':
		return request.GET[label]
	else:
		return request.POST[label]

def insert_db(request):
	data_f = get_web_data(request,'flag')
	db.insert_db(db_data,data_f)
	return HttpResponse('Data save to mongodb')

def lookup_db(request):
	data_f = get_web_data(request,'flag')
	query_list = db.query_db(data_f)
	res = ''
	if len(query_list)>1:
		res='<br>'.join(query_list)
	elif len(query_list)==1:
		res=query_list[0]
	else:
		res = "Can not find data in Database"
	return HttpResponse(res)

def delete_db(request):
	data_f = get_web_data(request,'flag')
	db.delete_data(data_f)
	return HttpResponse("Delete data from dataBase")

def test(request):  
    return render(request, 'index.html')

def process_data(request):
	seq = get_web_data(request,'seq')
	task = get_web_data(request,'task')
	if len(seq.strip()) == 0:
		res = 'NULL'
	else:
		res,_ = nlp(seq,task)
		global db_data
		db_data = copy.deepcopy(res)
		db_data['data']=seq
		res = json.dumps(res,ensure_ascii=False)
		logger.info(res)
		res = res.encode('utf-8')
	return HttpResponse(res)

def url_way(request):
	seq = get_web_data(request,'sentence')
	if len(seq.strip()) >=1:
		res,_ = nlp(seq,'')
		res = json.dumps(res,ensure_ascii=False)
		logger.info(res)
		res = res.encode('utf-8')
		return HttpResponse(res)
	else:
		return HttpResponse("Sorry,Check your input!!")

def url_way_test(request):
	seq = get_web_data(request,'sentence')
	task = get_web_data(request,'task')
	if len(seq.strip()) >=1:
		res,cls_seq = nlp(seq,task)
		res = json.dumps(res,ensure_ascii=False)
		logger.info(res)
		res = cls_seq + '\n' + res
		res = res.encode('utf-8')
		return HttpResponse(res)
	else:
		return HttpResponse("Sorry,Check your input!!")

def url_way_scene(request):
	seq = get_web_data(request,'sentence')
	if len(seq.strip()) >=1:
		res = scene(seq)
		res = json.dumps(res,ensure_ascii=False)
		logger.info(res)
		res = res.encode('utf-8')
		return HttpResponse(res)
	else:
		return HttpResponse("Sorry,Check your input!!")

def process_chat(request):
	seq = get_web_data(request,'sentence')
	if len(seq.strip()) == 0:
		res = 'NULL'
	else:
		res,_ = nlp(seq,'chat')
		logger.info(res)
		res = res.encode('utf-8')
	return HttpResponse(res)