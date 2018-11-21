# encoding=utf-8

def mode_and_replace(mmode, smode, sentence, mode=1):
    # [[], [], {}, ''],
    mode_befor = [[['all'], ['all'], {'亮':'嫌弃太亮', '太亮':'嫌弃太亮', '好亮':'嫌弃太亮', '刺眼':'嫌弃刺眼', '好刺眼':'嫌弃刺眼', '太刺眼':'嫌弃刺眼'}, 'f'],
                  [['all'], ['all'], {'暗':'嫌弃太暗', '太暗':'嫌弃太暗', '好暗':'嫌弃太暗'}, 'f'],
                  [['all'], ['all'], {'热':'嫌弃太热', '好热':'嫌弃太热', '太热':'嫌弃太热', '热死':'嫌弃太热', '爆热':'嫌弃太热'}, 'f'],
                  [['all'], ['all'], {'冷':'嫌弃太冷', '太冷':'嫌弃太冷', '好冷':'嫌弃太冷', '冷死':'嫌弃太冷', '冻死':'嫌弃太冷', '冻':'嫌弃太冷'}, 'f'],
                  [['all'], ['all'], {'上条':'上一条', '上个':'上一条', '下条':'下一条', '下个':'下一个'}, 'f'],
                  [['all'], ['all'], {'笨':'你太笨', '你笨':'你太笨', '太笨':'你太笨', '好笨':'你太笨', '蠢':'你太蠢', '太蠢':'你太蠢', '好蠢':'你太蠢', '蠢死':'你太蠢', '牛逼':'你牛逼', '傻逼':'你傻逼', '傻屌':'你傻逼'}, 'f'],
                  [['phone'], ['all'], {'打给': '呼叫', '发给': '发送给'},'p'],
                  ]

    mode_after = [[['home-applications'], ['air-conditioner'], {'desc ds-volumn value = negative':'set ds-volumn value = positive'}, 'f'],
                  [['home-applications'], ['air-conditioner'], {'desc ds-volumn value = positive':'set ds-volumn value = negative'}, 'f'],
                  [['home-applications'], ['air-conditioner'], {'desc ds-brightness value = positive':'set ds-brightness value = negative'}, 'f'],
                  [['home-applications'], ['air-conditioner'], {'desc ds-brightness value = negative':'set ds-brightness value = positive'}, 'p'],
                  [['all'], ['all'], {'call to': 'call', 'sms to': 'sms', 'reply to': 'reply','do to':'do','send to': 'send','compose to': 'compose', 'reply to': 'reply'}, 'p'],
                  [['phone'], ['call', 'sms'], {'call to': 'call', 'sms to': 'sms'}, 'p'],
                  [['tv'], ['all'], {'quite object':'set ds-volumn'}, 'p'],
                  ]

    if (mode == 1):
        for i in range(len(mode_befor)):
            if (mmode in mode_befor[i][0]):
                if (smode in mode_befor[i][1]):
                    if ('f' == mode_befor[i][3]):
                        for key in mode_befor[i][2]:
                            if (key == sentence):
                                sentence = mode_befor[i][2][key]
                                return sentence
                    if ('p' == mode_befor[i][3]):
                        for key in mode_befor[i][2]:
                            if (key in sentence):
                                sentence = sentence.replace(key, mode_befor[i][2][key])
                                return sentence



    if (mode == 2):
        for i in range(len(mode_after)):
            if (mmode in mode_after[i][0]):
                if (smode in mode_after[i][1]):
                    if ('f' == mode_after[i][3]):
                        for key in mode_after[i][2]:
                            if (key == sentence):
                                sentence = mode_after[i][2][key]
                                return sentence
                    if ('p' == mode_after[i][3]):
                        for key in mode_after[i][2]:
                            if (key in sentence):
                                sentence = sentence.replace(key, mode_after[i][2][key])
                                return sentence
    return sentence

def delete_end_word(sentence):
    end_label = [u'了', u'吧',u'啊',u'噻',u'呗',u'嗯']
    if (sentence.endswith('\n')):
        sentence = sentence.strip()[:-1]
    sentence = sentence.strip()
    while (sentence[-1] in end_label):
        sentence = sentence[:-1]
    return sentence


# 示例：
sent_na_p = mode_and_replace(mmode='all', smode='all', sentence='太亮', mode=1)
sent_na_f = mode_and_replace(mmode='all', smode='all', sentence='好看', mode=1)
sent_lf = mode_and_replace(mmode='all', smode='all', sentence='call to $object', mode=2)
sent_delete = delete_end_word(u'行了吧 ')
