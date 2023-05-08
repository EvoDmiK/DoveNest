import json
import os

from easydict import EasyDict as edict
from PyKakao import Message
import requests as req
import schedule

from misc.configs import *
from misc.utils import *

AUTH = CONFIG.kakao_auth
KEY  = CONFIG.kakao

N_CONTENTS = 3

MSG  = Message(service_key = KEY)
MSG.headers = {'Authorization' : AUTH}

header_title = "TODAY SALE INFORMATION"
header_link  = {
                    'web_url'        : 'https://store.steampowered.com/',
                    'android_execution_params' : 'main',
                    'ios_execution_params'     : 'main'
                }


sale_items   = get_sale_items(n_contents = 3)
length       = len(sale_items['data'])

## n_contents 재 계산식  N_CONTENS     +       (N_CONTENTS - length)     = 2 * N_CONTENTS - length
##                   (탐색 하려는 갯수)  + (탐색 하고자 하는 갯수 보다 모자란 정도)
sale_items   = sale_items if length == N_CONTENTS else \
               get_sale_items(n_contents = 2 * N_CONTENTS - length)


contents = []

for k, v in sale_items['data'].items():
    
    data = {
            'title'        : v['name'],
            'description'  : v['genre'],
            'image_url'    : v['image'],
            'image_width'  : 640,
            'image_height' : 640,

            'link'         : {
                                'web_url'        : v['steam_page'],
                                'mobile_web_url' : v['steam_page'],
                                'android_execution_params' : f'contents/{k}',
                                'ios_execution_params'     : f'contents/{k}'
                            } 
        }

    contents.append(data)


buttons = [{
                
            'title' : '자세한 정보',
            'link'  : {
                        'web_url'        : 'https://store.steampowered.com/',
                    }
            }  
        ]

MSG.send_list(
                header_title = header_title,
                header_link  = header_link,
                contents     = contents,
                buttons      = buttons
            )