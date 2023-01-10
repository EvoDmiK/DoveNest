from bs4 import BeautifulSoup as bs
from datetime import datetime
import requests as req
import schedule
import sqlite3
import json
import time
import os

ROOT_PATH = f'/config/workspace/project/DoveNest/informations/'
NOW     = datetime.now()
Y, M, D = NOW.year, NOW.month, NOW.day

TABLE_NAME = 'steamsale'
os.makedirs(f'{ROOT_PATH}/db/steam', exist_ok = True)

class saleDB:

    def connect_db():

        dbpath = f'{ROOT_PATH}/db/steam/{TABLE_NAME}.db'
        conn   = sqlite3.connect(dbpath)
        cursor = conn.cursor()

        return cursor, conn

    
    def create_table():
        
        cursor, _ = saleDB.connect_db()
        query = f"""
                    CREATE TABLE IF NOT EXISTS {TABLE_NAME}(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appid INTEGER NOT NULL,
                    percent INTEGER NOT NULL,
                    original INTEGER NOT NULL,
                    discounted INTEGER NOT NULL,
                    date DATE NOT NULL);
                """

        cursor.execute(query)
        return cursor


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
            with open(f'{ROOT_PATH}/db/steam/{TABLE_NAME}.sql', 'w') as f:
                for line in conn.iterdump():
                    f.write('%s\n' % line)

                print('[INFO] DB backup complete!')



## 스팀 세일 페이지에서 데이터 스크래핑 해서 가져오는 함수
def discount_scraping():
    whole_page = ""

    for idx in range(5):
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

    cursor = saleDB.create_table()
    sales  = discount_scraping()

    for idx, sale in enumerate(sales):
        try:
            appid      = sale['data-ds-appid']

            percent    = sale.select('.search_discount > span')[0].text
            percent    = int(percent.replace('-', '').replace('%', ''))

            original   = preprop(sale.select('strike')[0].text)
            discounted = preprop(sale.select(".discounted")[0].text, dtype="discount")
            
            today = f'{Y}-{str(M).zfill(2)}-{str(D).zfill(2)}'
            saleDB.insert_table(cursor, (appid, percent, original, discounted, today))
        
        except Exception as e: print(f'[error] {e}')

    query = "SELECT * FROM steamsale"
    cursor.execute(query)

    print(cursor.fetchall())
    saleDB.backup_table()

schedule.every(1).minutes.do(get_salelist)

while True:
    now = datetime.now()
    Y, M, D = now.year, now.month, now.day
    h, m    = now.hour, now.minute  

    schedule.run_pending()
    time.sleep(1)