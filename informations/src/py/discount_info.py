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
import pymysql as sql
import schedule
import redis

## 3. 직접 구현한 모듈
from misc import configs

## 전역 변수 지정
ITEMS_TAG = configs.ITEMS_TAG
CONFIGS   = configs.CONFIGS
LOGGER    = configs.LOGGER
PORTS     = configs.PORTS
URLS      = configs.URLS


PASSWD    = CONFIGS.sql_passwd
SPORT     = PORTS.sql_port
RPORT     = PORTS.redis_port
HOST      = CONFIGS.global_host
USER      = CONFIGS.sql_user

NOW       = datetime.now()
Y, M, D   = NOW.year, NOW.month, NOW.day

today     = f'{Y}{str(M).zfill(2)}{str(D).zfill(2)}'

## CONFIG 파일을 이용하여 Redis 서버에 연결
## decode_responses = True를 이용하면 key 값을 get 했을때 binary가 아닌 string으로 반환
rconn     = redis.Redis(host = HOST, port = RPORT,
                        decode_responses = True, db = 1)

## 할인 정보를 담고 있는 DB 클래스
class SaleDB:

    def __init__(self, host, user, passwd, port, db):
        
        LOGGER.info(f'[INFO] DB서버에 연결 중 입니다. 잠시만 기다려 주세요.')
        ## MariaDB 서버에서 DoveNest DB에 연결
        self.conn    = sql.connect(host = host, port = port, user = user,
                                   passwd = passwd, db = db)

        self.cursor = self.conn.cursor()
        LOGGER.info(f'[INFO] DB서버에 연결 되었습니다.')

    ## 테이블 생성함수
    def create_table(self):
        
        LOGGER.info(f'[INFO] 테이블을 생성 중 입니다. 잠시만 기다려 주세요.')
        query = f'''
                    CREATE TABLE IF NOT EXISTS discount_info(
                        idx        INTEGER NOT NULL,
                        appid      TEXT    NOT NULL,
                        title      TEXT    NOT NULL,
                        percent    INTEGER NOT NULL,
                        discounted TEXT    NOT NULL,
                        original   TEXT    NOT NULL,
                        platform   TEXT    NOT NULL,
                        storepage  TEXT,
                        thumbnail  TEXT,
                        date       TEXT NOT NULL
                    );
                '''

        self.cursor.execute(query)
        LOGGER.info('[INFO] 테이블 생성이 완료 되었습니다.\n')


    ## 데이터 입력 함수
    def insert_table(self, data_tuple):

        query = '''
                    INSERT INTO discount_info (idx, appid, title, percent,
                    discounted, original, platform, storepage, thumbnail, date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''

        self.cursor.execute(query, data_tuple)


    ## 테이블에 오늘 저장된 데이터 개수를 반환해주는 함수
    def __len__(self):

        return self.cursor.execute(f'select * from discount_info where date={today}')


## 할인 정보 페이지를 스크래핑 하는 함수
def scrapping(platform = 'steam'):

    LOGGER.info(f'[INFO] 현재 {platform} 할인 정보 페이지를 스크래핑 중입니다. 잠시만 기다려 주세요.')
    url = URLS[platform]

    ## 파라미터 값이 steam인 경우에는 10페이지까지 데이터를 삭 긁어옴.
    if platform == 'steam':

        res = ''
        for idx in range(1, 10):

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
    DB = SaleDB(HOST, USER, PASSWD, SPORT, 'DoveNest')

    if platform == 'steam': DB.create_table()

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
                json_      = json.loads(rconn.get(f'id:{appid}'))
                thumbnail  = json_['data']['header_image']

                percent     = item.select('.search_discount > span')[0].text
                percent     = clear(percent)

                original    = item.select('strike')[0].text.strip()
                discount    = item.select('.discounted')[0].text.split('₩')[-1]
                discount    = f'₩{discount}'

            elif platform == 'nintendo':
                
                title_link = item.select('a.category-product-item-title-link')
                store_page = title_link[0]['href']
                thumbnail  = item.select('span > img')[0]['data-src']
                original   = item.select('span > span.price')[1].text
                discount   = item.select('span > span.price')[0].text

                ## nintendo 할인 페이지에는 할인율을 제공하지 않아 직접 계산 
                percent    = 100 - round(clear(discount) * 100 / clear(original))
                title      = title_link[0].text.strip()

                # LOGGER.info(store_page)
                appid      = store_page.split('.kr/')[1]

            data_tuple = [idx + length, appid, title, percent, discount,
                         original, platform, store_page, thumbnail, today]

            DB.insert_table(data_tuple)

        except: LOGGER.error(format_exc())

    LOGGER.info(f'[INFO] DB에 모든 데이터 입력을 완료 했습니다.')
    LOGGER.info(f'[INFO] 현재 테이블에 저장된 데이터 개수는 {len(DB)}개 입니다.\n')
    DB.conn.commit()
    DB.conn.close()


## 매일 오전 10시 반에 데이터 가져오는 함수 실행
schedule.every().day.at("10:30").do(mining, 'steam')
schedule.every().day.at("10:30").do(mining, 'nintendo')


while True:

    schedule.run_pending()
    time.sleep(1)
