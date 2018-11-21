import numpy as np
import pickle

def sentence2matrix(sentences,max_length,vocs):
    sentences_num = len(sentences)
    data_dict = np.zeros((sentences_num,max_length),dtype='int32')

    for index,sentence in enumerate(sentences):
        data_dict[index,:]=map2id(sentence,vocs,max_length)

    return data_dict


def map2id(sentence,voc,max_len):
    array_int = np.zeros((max_len,),dtype='int32')
    min_range = min(max_len,len(sentence))

    for i in range(min_range):
        item = sentence[i]
        array_int[i] = voc.get(item,voc['<unk>'])

    return array_int


def batch_iter(data, batch_size, num_epochs, shuffle=True):
    data = np.array(data)
    data_size = len(data)
    num_batches_per_epoch = int((len(data)-1)/batch_size) + 1

    for epoch in range(num_epochs):
        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indices]
        else:
            shuffled_data = data
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)

            yield shuffled_data[start_index:end_index]

def read_data_from_str(line,max_sentence_length):
    line = line.decode('utf-8')
    line = ''.join([word + ' ' for word in line])
    line = line.strip().lower()
    line=line.split(' ')

    if len(line) > max_sentence_length:
        line = line[:max_sentence_length]
    else:
        line.extend(['<pad>'] * (max_sentence_length - len(line)))

    return [line]


def read_data_from_strs(lines,max_sentence_length):
    data_line = []

    for line in lines:
        line = line.decode('utf-8')
        line = ''.join([word + ' ' for word in line])
        line = line.strip().lower()
        line=line.split(' ')

        if len(line) > max_sentence_length:
            line = line[:max_sentence_length]
        else:
            line.extend(['<pad>'] * (max_sentence_length - len(line)))

        data_line.append(line)

    return data_line


def read_vocabulary(voc_dir):

    voc = dict()
    lines = open(voc_dir,'r').readlines()

    for i in range(len(lines)):
        key = lines[i].decode('utf-8').split('\n')[0]
        voc[key] = i

    print 'read vocabulary len : %f'%len(voc.keys())
    return voc,len(voc.keys())
