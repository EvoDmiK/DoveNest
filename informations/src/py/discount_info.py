from bs4 import BeautifulSoup as bs
from datetime import datetime
import requests as req
import schedule
import sqlite3
import json
import time
import os

ROOT_PATH = f'/config/workspace/project/DoveNest/informations/'

TABLE_NAME = 'saleinfo'
DB_NAME    = 'game_informations'

os.makedirs(f'{ROOT_PATH}/db', exist_ok = True)

class saleDB:

    ## DB와 연결시켜주는 함수
    def connect_db():

        dbpath = f'{ROOT_PATH}/db/{DB_NAME}.db'
        conn   = sqlite3.connect(dbpath)
        cursor = conn.cursor()

        return cursor, conn

    ## 테이블 만들어주는 함수
    def create_table():
        
        cursor, conn = saleDB.connect_db()
        query = f"""
                    CREATE TABLE IF NOT EXISTS {TABLE_NAME}(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appid INTEGER NOT NULL,
                    percent INTEGER NOT NULL,
                    original INTEGER NOT NULL,
                    discounted INTEGER NOT NULL,
                    platform TEXT NOT NULL, 
                    date TEXT NOT NULL);
                """

        cursor.execute(query)
        return cursor, conn


    ## 테이블에 데이터 입력해주는 함수
    def insert_table(cursor, data_tuple):
        
        appid, title, percent, origianl, discounted, date = data_tuple
        query = f"""
                    INSERT INTO {TABLE_NAME}
                    (appid, percent, original, discounted, date)
                    VALUES({appid}, {percent}, {original}, {discounted}, {today});
                """

        cursor.execute(query)


    ## 테이블 백업시켜주는 함수
    def backup_table():
        
        _, conn = saleDB.connect_db()
        with conn:
            with open(f'{ROOT_PATH}/db/{DB_NAME}.sql', 'w') as f:
                for line in conn.iterdump():
                    f.write('%s\n' % line)

                print('[INFO] DB backup complete!')


## 스팀 세일 페이지에서 데이터 스크래핑 해서 가져오는 함수
def discount_scraping():
    whole_page = ""

    ## 총 5페이지 긁어옴.
    for idx in range(1, 10):
        url = f'https://store.steampowered.com/search/?specials=1&filter=topsellers&page={idx}'
        res = req.get(url)
        whole_page += res.text

    soup       = bs(whole_page, 'html.parser')
    sales      = soup.select('div#search_resultsRows > a') 

    return sales


## 원래 가격, 할인된 가격에서 필요없는 부분 전처리 해주는 함수
def preprop(string, dtype = 'discount'): 
    
    if dtype == 'discount': string = string.replace(' ', '').split('₩')[-1]
    string = string.replace(',', '').replace('₩', '')
    
    return int(string)


## 스크래핑 된 데이터에서 필요한 정보만 긁어오는 함수
def get_salelist(): 
    NOW     = datetime.now()
    Y, M, D = NOW.year, NOW.month, NOW.day

    cursor, conn = saleDB.create_table()
    sales        = discount_scraping()

    for idx, sale in enumerate(sales):
        try:
            appid      = sale['data-ds-appid']

            percent    = sale.select('.search_discount > span')[0].text
            percent    = int(percent.replace('-', '').replace('%', ''))

            original   = preprop(sale.select('strike')[0].text)
            discounted = preprop(sale.select(".discounted")[0].text, dtype="discount")
            
            today = f'{Y}{str(M).zfill(2)}{str(D).zfill(2)}'

            query = f"""
            INSERT INTO {TABLE_NAME}
            (appid, percent, original, discounted, platform, date)
            VALUES({appid}, {percent}, {original}, {discounted}, 'steam', {today});
            """
            cursor.execute(query)


        except Exception as e: print(f'[error] {e}')

    query = f"SELECT * FROM {TABLE_NAME}"
    cursor.execute(query)

    conn.commit()
    saleDB.backup_table()



# ## 매일 오전 10시에 데이터 가져오는 함수 실행
schedule.every().day.at("10:00").do(get_salelist)

while True:

    schedule.run_pending()
    time.sleep(1)