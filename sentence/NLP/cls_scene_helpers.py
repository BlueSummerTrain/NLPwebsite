import numpy as np
import config as cf
import web_mode_config as wf
'''
scene cls data process relate code define here
get_batch_data is the last function
'''
def read_vocabulary(voc_dir):
	voc = dict()
	lines = open(voc_dir, 'r').readlines()
	for i in range(len(lines)):
		key = lines[i].decode('utf-8').split('\n')[0]
		voc[key] = i
	return voc

def sentence2matrix(sentences, max_length, vocs):
	sentences_num = len(sentences)
	data_dict = np.zeros((sentences_num, max_length), dtype='int32')

	for index, sentence in enumerate(sentences):
		data_dict[index, :] = map2id(sentence, vocs, max_length)

	return data_dict

def map2id(sentence, voc, max_len):
	array_int = np.zeros((max_len,), dtype='int32')
	min_range = min(max_len, len(sentence))

	for i in range(min_range):
		item = sentence[i]
		array_int[i] = voc.get(item, voc['<unk>'])

	return array_int

def read_data_from_strs(lines, max_sentence_length):
	data_line = []

	for line in lines:
		line = line.decode('utf-8')
		line = ''.join([word + ' ' for word in line])
		line = line.strip().lower()
		line = line.split(' ')

		if len(line) > max_sentence_length:
			line = line[:max_sentence_length]
		else:
			line.extend(['<pad>'] * (max_sentence_length - len(line)))

		data_line.append(line)
	return data_line

def batch_iter(data, batch_size, num_epochs, shuffle=True):
	data = np.array(data)
	data_size = len(data)
	num_batches_per_epoch = int((len(data)-1)/batch_size) + 1

	for epoch in range(num_epochs):
		if shuffle:
			shuffle_indices = np.random.permutation(np.arange(data_size))
			shuffled_data = data[shuffle_indices]
		else:
			shuffled_data = data
		for batch_num in range(num_batches_per_epoch):
			start_index = batch_num * batch_size
			end_index = min((batch_num + 1) * batch_size, data_size)
			yield shuffled_data[start_index:end_index]

def get_batch_data(data_item, vocab,max_len):
	BATCH_SIZE = 16 # set default batch size
	data = []
	if type(data_item) == str or type(data_item) == unicode:
		data.append(data_item)
	elif type(data_item) == list:
		data = data + data_item
	else:
		raise 'scene input data wrong,list or str'

	data = read_data_from_strs(data, max_len)
	x_test = sentence2matrix(data, max_len, vocab)
	batchs = batch_iter(x_test, BATCH_SIZE, 1, shuffle=False)
	return batchs
'''
scene config code define here 
'''
Data_tup_tv = [(['tv_control.data'], 0, 'tv_control'),

               (['app_control.data'], 1, 'app_control'),

               (['video.data'], 2, 'video'),

               (['weather.data'], 3, 'weather'),

               (['channel_switch.data'], 4, 'channel_switch'),

               (['image_scene_interactive.data'], 5, 'image_scene_interactive'),

               (['math_operation.data'], 6, 'math_operation'),

               (['disport.data'], 7, 'disport'),

               (['time_query.data'], 8, 'time_query'),

               (['encyclopedia_information.data'], 9, 'encyclopedia_information'),

               (['info_query_news.data'], 10, 'info_query_news'),

               (['stock_fund_information.data'], 11, 'info_query_stock&fund'),

               (['translation.data'], 12, 'translate'),

               (['converter.data'], 13, 'converter'),

               (['karaoke.data'], 14, 'karaoke'),

               (['household_appliance_control.data'],
                15, 'household_appliance_control'),

               (['music_on_demand.data'], 16, 'music_on_demand'),

               (['scenic_spot.data'], 17, 'scenic_spot'),

               (['restaurant.data'], 18, 'restaurant'),

               (['takeout.data'], 19, 'takeout'),

               (['map_server.data'], 20, 'map_server'),

               (['cinema_ticket.data'], 21, 'cinema_ticket'),

               (['hotel_reservation.data'], 22, 'hotel_reservation'),

               #(['third_info_query.data'], 23, 'third_info_query'),

               (['travel_booking.data'], 23, 'travel_booking'),

               (['shopping.data'], 24, 'shopping'),

               (['multi-turn_dialogue.data'], 25, 'multi-turn_dialogue'),

               # (['unknown.data'], 26, 'unknown'),

               # (['chat.data'], 27, 'chat'),

               (['unknown.data','chat.data'], 26, 'unknown'),

               (['media.data'], 27, 'media')
               ]

Data_tup_ngtv = [(['play_control.data', 'tv_setting_and_state_query.data',
                 'ngtv_tv_control.data'], 0, 'tv_control'),

               (['film.data', 'tv_play.data', 'programme.data', 'normal_video.data',
                 'history.data', 'traditional_opera.data', 'acrobatics.data',
                 'short_sketch.data', 'comic_dialogue.data', 'education.data',
                 'cartoon.data', 'sports.data', 'mixed_video.data'], 1, 'video'),

               (['basic_weather.data', 'basic_rate.data',
                 'disaster_warn.data', 'mixed_weather.data'], 2, 'weather'),

               (['channel_switch.data', 'ngtv_channel_switch.data'],
                3, 'channel_switch'),

               (['image_scene_interactive.data', 'ngtv_image_scene_interactive.data'],
                4, 'image_scene_interactive'),

               (['photograph.data'], 5, 'photograph'),

               (['find_obj.data'], 6, 'find_obj'),

               (['scenic_spots_ticket.data', 'scenic_spots_recommend.data',
                 'mixed_scenic_spot.data', 'ngtv_scenic.data'], 7, 'scenic_spot'),

               (['restaurant_reservation.data', 'restaurant_recommend.data',
                 'mixed_restaurant.data'], 8, 'restaurant'),

               (['shopping.data'], 9, 'shopping'),

               (['map_server.data'], 10, 'map_server'),

               (['unknown.data', 'chat.data'], 11, 'unknown'),

               ]

def translate_readable_logit(logit, num):
    Data_tup_tv_predict = Data_tup_tv
    if wf.CONFIG_MODE == 'ngtv':
      Data_tup_tv_predict = Data_tup_ngtv

    predict_index = logit.index(max(logit))
    predict = Data_tup_tv_predict[predict_index][2]
    logit_tuplist = []
    logit_label_list = []
    for i in range(len(Data_tup_tv_predict)):
        logit_label_list.append(Data_tup_tv_predict[i][2])
    for i in range(len(logit)):
        logit_tuplist.append((logit_label_list[i], float('%.2f' % logit[i])))
    logit_tuplist.sort(key=lambda x: x[1], reverse=True)
    high_logits = logit_tuplist[:num]
    res_list = []
    for item in high_logits:
    	res_list.append({item[0]:item[1]})
    return res_list
