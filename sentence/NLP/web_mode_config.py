# model exclude conditions
TV_MODE = 'tv'  # tv mode
PHONE_MODE = 'phone'  # phone mode
NTV_MODE = 'newtv'  # new branch tv
NGTV_MODE = 'ngtv'
HOME_MODE = 'home'

# for open-domain chatting
CHAT_MODE = 'chat'

CONFIG_MODE = NTV_MODE  # default mode is tv
# config path
import os
CONFIG_PATH = os.getcwd() + '/sentence/NLP/conf/%s.command.conf' % (CONFIG_MODE)
# NLP version number
version = 'v1.1.7'
