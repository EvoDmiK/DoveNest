## 필요한 패키지들 로드
## 1. 내장 모듈
from traceback import format_exc
from datetime import datetime
import json
import time
import os
import re

## 2. 써드 파티 패키지
from easydict import EasyDict as edict
from bs4 import BeautifulSoup as bs
import requests as req
import schedule
import redis

## 3. 직접 구현한 모듈
from misc.DataBase import _DB, _RedisDB
from misc import configs


## 전역 변수 지정
ITEMS_TAG = configs.ITEMS_TAG
LOGGER    = configs.LOGGER
URLS      = configs.URLS

RCONN     = _RedisDB(db_idx = 1)

NOW       = datetime.now()
Y, M, D   = NOW.year, NOW.month, NOW.day
TODAY     = f'{Y}{str(M).zfill(2)}{str(D).zfill(2)}'


## 할인 정보 페이지를 스크래핑 하는 함수
def scrapping(platform = 'steam'):

    LOGGER.info(f'[INFO] 현재 {platform} 할인 정보 페이지를 스크래핑 중입니다. 잠시만 기다려 주세요.')
    url = URLS[platform]

    ## 파라미터 값이 steam인 경우에는 30페이지까지 데이터를 삭 긁어옴.
    if platform == 'steam':

        res = ''
        for idx in range(1, 30):

            url_  = f'{url}{idx}'
            res += req.get(url_).text

    ## nintendo인 경우에는 그냥 데이터를 삭 긁어옴.
    elif platform == 'nintendo':
        res = req.get(url).text


    soup = bs(res, 'html.parser')
    LOGGER.info(f'[INFO] {platform} 할인 정보 페이지 스크래핑을 완료했습니다.\n')

    ## 각 platform별 할인정보를 담고 있는 태그 파싱
    return soup.select(ITEMS_TAG[platform])
    

## 파싱된 데이터에서 필요한 데이터만 뽑아서 DB에 입력하는 함수
def mining(platform = 'steam'):

    DB = _DB('DoveNest', 'discount_info')    
    DB.create_table([
                    ['appid'     ,    'TEXT', True],
                    ['title'     ,    'TEXT', True],
                    ['percent'   , 'INTEGER', True],
                    ['discounted',    'TEXT', True],
                    ['original'  ,    'TEXT', True],
                    ['platform'  ,    'TEXT', True],
                    ['storepage' ,    'TEXT', False],
                    ['thumbnail' ,    'TEXT', False],
                    ['date'      ,    'TEXT', True],
                    ['review'    ,    'TEXT', False]
            ])

    items      = scrapping(platform)
    clear      = lambda x: int(re.sub('[^0-9]*', '', x))
    length     = len(DB)

    LOGGER.info(f'[INFO] 현재 스크래핑 한 데이터에서 필요한 정보를 DB에 입력 중 입니다.')
    LOGGER.info(f'[INFO] 현재 테이블에 저장된 데이터 개수는 {length}개 입니다.\n')
    for idx, item in enumerate(items, 1):
        '''
            DB에 저장할 데이터는
            idx        | 데이터의 인덱스 값
            appid      | 할인 품목의 고유 아이디
            title      | 할인 품목의 이름
            percent    | 할인율
            discount   | 할인가
            original   | 원가
            platform   | 할인 플랫폼
            store_page | 할인 물품의 상점 페이지
            thumbnail  | 할인 품목의 이미지
            date       | 오늘 날짜
        '''

        try:
            if platform == 'steam':

                appid      = item['data-ds-appid']
                title      = item.select('span.title')[0].text
                store_page = f'https://store.steampowered.com/app/{appid}'
                
                ## 스크래핑 해 본 결과 이미지가 없어서 redis에 저장되어 있는 데이터로 사용
                json_      = json.loads(RCONN.get(f'id:{appid}'))
                thumbnail  = json_['data']['header_image']

                block       = item.select('.discount_block')[0]
                percent     = block.select('.discount_pct')[0].text
                percent     = clear(percent)

                original    = block.select('.discount_original_price')[0].text.strip()
                discount    = block.select('.discount_final_price')[0].text.split('₩')[-1]
                discount    = f'₩{discount}'

                try: 
                    review = item.select('.search_review_summary')[0]
                    review = review['data-tooltip-html'].replace('<br>', ' ')

                except: review = None
            
            elif platform == 'nintendo':
                
                title_link = item.select('a.category-product-item-title-link')
                store_page = title_link[0]['href']
                thumbnail  = item.select('span > img')[0]['data-src']
                original   = item.select('span > span.price')[1].text
                discount   = item.select('span > span.price')[0].text

                ## nintendo 할인 페이지에는 할인율을 제공하지 않아 직접 계산 
                percent    = 100 - round(clear(discount) * 100 / clear(original))
                title      = title_link[0].text.strip()
                review     = None

                ## nintendo 스토어 할인 페이지에는 따로 appid가 없어
                ## 페이지 링크에 존재하는 데이터를 이용해 사용
                appid      = store_page.split('.kr/')[1]

            data_tuple = [
                            ['idx'       , idx + length],
                            ['appid'     ,        appid],
                            ['title'     ,        title],
                            ['percent'   ,      percent],
                            ['discounted',     discount],
                            ['original'  ,     original],
                            ['platform'  ,     platform],
                            ['storepage' ,   store_page],
                            ['thumbnail' ,    thumbnail],
                            ['date'      ,        TODAY],
                            ['review'    ,       review]
                        ]
            DB.insert_table(data_tuple)

        except: LOGGER.error(format_exc())

    LOGGER.info(f'[INFO] DB에 모든 데이터 입력을 완료 했습니다.')
    LOGGER.info(f'[INFO] 현재 테이블에 저장된 데이터 개수는 {len(DB)}개 입니다.\n')

    DB.commit()


## 매일 오전 10시 반에 데이터 가져오는 함수 
schedule.every().day.at("10:05").do(mining, 'steam')
schedule.every().day.at("10:05").do(mining, 'nintendo')


while True:

    schedule.run_pending()
    time.sleep(1)
