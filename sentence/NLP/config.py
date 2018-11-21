#coding=utf-8
#tag name
NAME = u'\u1401'
NUM = u'\u1405'
TI = u'\u1402'
TV_CH = u'\u1573'
APP = u'\u1436'
LOC = u'\u146d'
PER = u'\u144c'
ORG = u'\u144d'
GOODS = u'\u1453'
MEDIA = u'\u1465'
HOTEL = u'\u1468'
FOOD = u'\u15e3'
MONEY = u'\u15e4'
trans_tag_dict = {'NAME':NAME,'NUM':NUM,'TI':TI,'ATV':TV_CH,\
					'APP':NAME,'LOC':NAME,'PER':NAME,'ORG':NAME,\
					'GOODS':NAME,'MEDIA':NAME,'FOOD':NAME,'HOTEL':NAME,\
					'MONEY':NAME}

trans_tag_dict_scene = {'NAME':NAME,
						'NUM':NUM,
						'TI':TI,
						'ATV':TV_CH,
						'APP':APP,
						'LOC':LOC,
						'PER':PER,
						'ORG':ORG,
						'GOODS':GOODS,
						'MEDIA':MEDIA,
						'FOOD':FOOD,
						'HOTEL':HOTEL,
						'MONEY':MONEY}
#Chinese Number
ch_nums = {\
		'零'.decode('utf-8'):'0',\
		'一'.decode('utf-8'):'1',\
		'二'.decode('utf-8'):'2',\
		'两'.decode('utf-8'):'2',\
		'三'.decode('utf-8'):'3',\
		'四'.decode('utf-8'):'4',\
		'五'.decode('utf-8'):'5',\
		'六'.decode('utf-8'):'6',\
		'七'.decode('utf-8'):'7',\
		'八'.decode('utf-8'):'8',\
		'九'.decode('utf-8'):'9'
		}
ch_num_unit ={\
		'十'.decode('utf-8'):'10',\
		'廿'.decode('utf-8'):'20',\
		'百'.decode('utf-8'):'100',\
		'千'.decode('utf-8'):'1000',\
		'万'.decode('utf-8'):'10000',\
		'亿'.decode('utf-8'):'100000000'}
decimal_tag = '点'.decode('utf-8')
ten_thous = '万'.decode('utf-8')
point_bilion = '亿'.decode('utf-8')
#NMT label
Name_labels = ['$object','$gobj','$vobj','$movie',\
				'$micro-movie','$music','$actor',\
				'$person','$singer','$video',\
				'$app','$tv-play','$tv-variety',\
				'$cartoon','$ebook','$grand-movie',\
				'$music-opera','$mv','$director',\
				'$position','$opera', '$short-sketch', '$cross-talk',\
				'$acleaner','$ac']
Num_labels = ['$number']
Ti_labels = ['$ti']
atv_labels = ['$channel']
mutil_words = ['$list series','$lamp upward','$lamp ds-saturation']
#NMT data used
SRC_MAX_LENGTH = 35
TGT_MAX_LENGTH = SRC_MAX_LENGTH * 3
NMT_UNK_ID = 0
NMT_SOS_ID = 1
NMT_EOS_ID = 2
PADDING = 3

BUCKET_ID = 0
BATCH_STEP = 0

#model parameter
### Text Classify Web Model define #####
CF_FROZEN_MODEL = 'cls/cls.pb'
CF_VOC_PATH = 'cls/vocab'
CF_INPUT_NODE_1 = 'input_data:0'
CF_OUTPUT_NODE_1 = 'logit/logit:0'
### Text Classify end ##################

### scene Classify Web Model define #####
SCENE_PATH = "scene/cls_scene.pb"
SCENE_VOCAB_PATH = "scene/vocab"
SCENE_INPUT_NODE = 'input_data:0'
SCENE_OUTPUT_NODE = 'logit/logit:0'
SCENE_MAX_LENGTH = 32
### scene Classify end ##################

### scene cnn Classify Web Model define #####
SCENECNN_PATH = "scene_cnn/cls_scene.pb"
SCENECNN_VOCAB_PATH = "scene_cnn/vocab"
SCENECNN_INPUT_NODE0 = 'input_data:0'
SCENECNN_INPUT_NODE1 = 'dropout_keep_prob:0'
SCENECNN_OUTPUT_NODE = 'output/cf_softmax:0'
SCENECNN_MAX_LENGTH = 32
### scene Classify end ##################

### tct name Classify Web Model define #####
TCTNAME_PATH = "cls_name/cls_name.pb"
TCTNAME_VOCAB_PATH = "cls_name/vocab"
TCTNAME_INPUT_NODE = 'input_data:0'
TCTNAME_OUTPUT_NODE = 'logit/logit:0'
TCTNAME_MAX_LENGTH = 32
NAME_DICT = {0:'person',1:'place',2:'app'}
### tct name Classify end ##################

### NER Web Model define #####
NER_INPUT_NODE_1 = 'encoder_input_data:0'
NER_OUTPUT_NODE_1 = 'NER_output:0'
NER_INPUT_LEN = 40
### NER end ##################

### NMT Web Model define ####
NMT_FROZEN_MODEL = 'nmt/frozen_nmt.pb'
# input node format : input-node-name + ":" + 0 (0 is the index, usually as 0)
NMT_INPUT_NODE_1 = 'encoder_input_data:0'
NMT_INPUT_NODE_2 = 'seq_length_encoder_input_data:0'
NMT_OUTPUT_NODE_1 = 'model_output:0'
# vocabulary files.
DATA_VOCAB_FILE = 'nmt/vocab.na.data'
LABEL_VOCAB_FILE = 'nmt/vocab.lf.data'
### NMT end #################


### CHAT Web Model define ###
CHAT_FROZEN_MODEL = 'chat/frozen_chat.pb'

CHAT_INPUT_NODE_1 = 'encoder_input_data:0'
CHAT_INPUT_NODE_2 = 'seq_length_encoder_input_data:0'
CHAT_OUTPUT_NODE_1 = 'model_output:0'

CHAT_NA_VOCAB_FILE = 'chat/vocab.na.data'
CHAT_LF_VOCAB_FILE = 'chat/vocab.lf.data'
### CHAT end ###
