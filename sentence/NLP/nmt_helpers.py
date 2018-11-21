import codecs
import numpy as np
import config as cf

def nmt_get_string_by_index(rnn_output,tgt_datas_rev_vocab):
    if (tgt_datas_rev_vocab == None):
        return ''
    
    output_len = len(rnn_output)
    res_str = ''
    for i in range(output_len):
        out = rnn_output[i]
        for j in range(len(out)):
            t = tgt_datas_rev_vocab[out[j]]
            if (t != u'</s>'):
                res_str += t
                res_str += u' '
        if (res_str.endswith(u' ')):
            res_str = res_str[:-1]
        res_str += u'\n'
    if (res_str.endswith(u'\n')):
        res_str = res_str[:-1]
    return res_str


def nmt_convert_to_ids_by_single(sentence,src_datas_vocab):
    if (sentence == None or sentence == ''):
        return None, None
    seq = []
    seq_len = []
    sentence = sentence.encode('utf-8')
    if (False): #sentence.isalpha()
        word = sentence
        d_id = 0
        if (src_datas_vocab.has_key(word)):
            d_id = src_datas_vocab[word]
        seq.append(d_id)
        seq += [cf.NMT_EOS_ID]
        seq_len.append(len(seq))
    else:
        sentence = sentence.decode('utf-8')
        sentence = sentence[:cf.SRC_MAX_LENGTH]
        for word in sentence:
            d_id = 0
            if (src_datas_vocab.has_key(word)):
                d_id = src_datas_vocab[word]
            seq.append(d_id)
        seq += [cf.NMT_EOS_ID]
        seq_len.append(len(seq))
    seq = np.array(seq, dtype=np.int32)
    seq_len = np.array(seq_len, dtype=np.int32)
    seq = seq.reshape(1, -1)
    return seq, seq_len

def init_nmt_vocab(src_vocab_file, tgt_vocab_file):
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
