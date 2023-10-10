from traceback import format_exc
from datetime import datetime
import json
import time
import os
import re

from easydict import EasyDict as edict
from bs4 import BeautifulSoup as bs
import requests as req
import pymysql as sql
import redis

from misc import configs

CONFIGS = configs.CONFIGS
LOGGER  = configs.LOGGER
PORTS   = configs.PORTS

PASSWD  = CONFIGS.sql_passwd
SPORT   = PORTS.sql_port
RPORT   = PORTS.redis_port
HOST    = CONFIGS.global_host
USER    = CONFIGS.sql_user

NOW     = datetime.now()
Y, M, D = NOW.year, NOW.month, NOW.day
TODAY   = f'{Y}{str(M).zfill(2)}{str(D).zfill(2)}'

class _DB:

    def __init__(self, db, table):
        self.table  = table
        self.db     = db

        self.connect_db()


    ## DB 서버에 연결해주는 생성자 함수
    def connect_db(self):
        try:
            LOGGER.info('[INFO] DB 서버에 연결 중 입니다. 잠시만 기다려 주세요.')
            self.conn   = sql.connect(host = HOST, port = SPORT, user = USER,
                                    passwd = PASSWD, db = self.db)

            self.cursor = self.conn.cursor()
            LOGGER.info('[INFO] DB서버에 연결 되었습니다.\n')

        except:
            LOGGER.error('[ERROR] DB 서버 연결에 실패 했습니다. 다시 시도 바랍니다.\n')


    ## 테이블을 생성해주는 함수
    def create_table(self, columns):

        LOGGER.info('[INFO] 테이블을 생성 중 입니다. 잠시만 기다려 주세요.')
        query = f'''
                    CREATE TABLE IF NOT EXISTS {self.table}
                    (idx INTEGER NOT NULL,  
                '''
        for idx, column in enumerate(columns, 1):

            name, dtype, is_null = column
            q                    = f'{name} {dtype}' if is_null == False \
                                    else f'{name} {dtype} NOT NULL'

            query += f' {q},' if idx != len(columns) else f'{q})'

        self.cursor.execute(query)
        self.conn.commit()

        LOGGER.info('[INFO] 테이블 생성이 완료 되었습니다.\n')


    def insert_table(self, data_tuple):
        try:
            columns = ', '.join([data[0] for data in data_tuple])
            q       = ', '.join(['%s' for _ in enumerate(data_tuple)])        
        
            query = f'INSERT INTO {self.table} ({columns}) VALUES ({q})'
            self.cursor.execute(query, [data[1] for data in data_tuple])
        
        except Exception as e:
            LOGGER.error(f'[ERROR] 데이터를 입력하지 못했습니다. 쿼리 확인 부탁드립니다. {e}')

    
    def commit(self):
        self.conn.commit()
        self.conn.close()


    def backup_db(self):
        raise NotImplementedError


    def __len__(self):

        return self.cursor.execute(f'select * from {self.table} where date={TODAY}')


class _RedisDB:

    def __init__(self, db_idx = 1):
        ## CONFIG 파일을 이용하여 Redis 서버에 연결
        ## decode_responses = True를 이용하면 key 값을 get 했을때 binary가 아닌 string으로 반환
        self.rconn = redis.Redis(host = HOST, port = RPORT,
                                 decode_responses = True, db = db_idx)

    
    def get(self, data):

        return self.rconn.get(data)

if __name__ == '__main__':

    db = _DB('DoveNest', 'test')
    db.create_table([
                     ['appid', 'INTEGER', True],
                     ['name', 'TEXT', True],
                     ['json_data', 'TEXT', True]
                     ])

    db.insert_table([
                        ['idx', 0],
                        ['appid', 12345],
                        ['name', 'dove'],
                        ['json_data', 'dove']
                    ])
    
    db.commit()