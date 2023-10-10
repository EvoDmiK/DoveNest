from traceback import format_exc
from datetime import datetime
import json
import time
import os
import re

from easydict import EasyDict as edict
from bs4 import BeautifulSoup as bs
import requests as req
import schedule

from misc.DataBase import _DB
from misc import configs

ITEMS_TAG = configs.ITEMS_TAG
CONFIGS   = configs.CONFIGS
LOGGER    = configs.LOGGER
PORTS     = configs.PORTS
URLS      = configs.URLS

NOW       = datetime.now()
Y, M, D   = NOW.year, NOW.month, NOW.day
TODAY     = f'{Y}{str(M).zfill(2)}{str(D).zfill(2)}'


def scrapping(platform = 'steam'):

    LOGGER.info(f'[INFO] 현재 {platform} 출시 정보 페이지를 스크래핑 중입니다. 잠시만 기다려주세요.')
    url = URLS[f'{platform}_rel']

    res = req.get(url).text
    soup = bs(res, 'html.parser')

    LOGGER.info(f'[INFO] {platform} 출시 정보 페이지 스크래핑을 완료했습니다.\n')
    return soup.select(ITEMS_TAG[f'{platform}_rel'])


def mining(platform = 'steam'):

    DB        = _DB('DoveNest', 'release_info')    
    if platform == 'steam':
        DB.create_table([
                        ['title',     'TEXT', True],
                        ['rel_date',  'TEXT', True],
                        ['platform',  'TEXT', True],
                        ['thumbnail', 'TEXT', False],
                        ['date',      'TEXT', True]
                    ])

    items  = scrapping(platform)

    clear  = lambda x : re.sub('[^\uAC00-\uD7A3.0-9a-zA-Z\s]', '', x)
    length = len(DB)

    LOGGER.info(f'[INFO] 현재 스크래핑 한 데이터에서 필요한 정보를 DB에 입력 중 입니다.')
    LOGGER.info(f'[INFO] 현재 테이블에 저장된 데이터 개수는 {length}개 입니다.\n')

    try:
        item_tag    = 'a.tab_item' if platform == 'steam' else 'li'
        
        for idx, item in enumerate(items[0].select(item_tag), 1):

            if platform == 'steam':
                title     = item.select('div.tab_item_name')[0].text
                thumbnail = item.select('img.tab_item_cap_img')[0]['src']

                rel_date  = item.select('div.release_date')[0].text
                rel_date  = rel_date if rel_date != '' else '미정'

            elif platform == 'nintendo':
                thumbnail = item.select('img')[0]['src']
                thumbnail = f'https://www.nintendo.co.kr{thumbnail}'

                title     = clear(item.select('.device-switch')[0].text.strip())
                developer = clear(item.select('.rel-maker')[0].text.strip())
                rel_date  = clear(item.select('.rel-date')[0].text.strip())
                rel_date  = rel_date if rel_date != '' else '미정'

            data_tuple = [
                            ['idx'      , idx + length],
                            ['title'    , title],
                            ['rel_date' , rel_date],
                            ['platform' , platform],
                            ['thumbnail', thumbnail],
                            ['date'     , TODAY]
                        ]
            DB.insert_table(data_tuple)

        LOGGER.info(f'[INFO] DB에 모든 데이터 입력을 완료 했습니다.')
        LOGGER.info(f'[INFO] 현재 테이블에 저장된 데이터 개수는 {len(DB)}개 입니다.\n')


    except: LOGGER.error(format_exc())
    DB.commit()


schedule.every().day.at("10:00").do(mining, 'steam')
schedule.every().day.at("10:00").do(mining, 'nintendo')

while True:

    schedule.run_pending()
    time.sleep(1)

