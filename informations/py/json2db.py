from multiprocessing import Pool, Process
from imutils.paths import list_files
from datetime import datetime
import sqlite3 as sql
from tqdm import tqdm
import json
import time
import os

ROOT_PATH = f'/config/workspace/project/DoveNest/informations'
JSON_PATH = f'{ROOT_PATH}/jsons'
DB_PATH   = f'{ROOT_PATH}/db'

DB_NAME    = 'game_informations'
# DB_NAME    = 'test'
TABLE_NAME = 'games'

load_json = lambda path: json.loads(open(path, 'r').read())

class _DB:
    
    def __init__(self, db_name, table_name, columns):
        
        self.db_name    = db_name
        self.columns    = columns
        self.table_name = table_name
        
        self.conn, self.cursor = self.conn_db()
        
        
    def conn_db(self):
        
        conn   = sql.connect(f'{DB_PATH}/{self.db_name}.db', timeout = 3600.0)
        cursor = conn.cursor()
        
        return conn, cursor
    
    
    def create_table(self):
        
        query = f'''
                    CREATE TABLE IF NOT EXISTS {self.table_name}(
                    
                '''
        
        for idx, column in enumerate(self.columns, 1):
            
            name, dtype, is_null = column
            q      = f'{name} {dtype}' if is_null == False \
                    else f'{name} {dtype} NOT NULL'
            query += f'\t{q},\n' if idx != len(self.columns) \
                     else f'{q})'

        self.cursor.execute(query)
        self.conn.commit()
    
    
    def insert_table(self, data_tuple):
        
        q = ''
        for idx, data in enumerate(data_tuple, 1):
            q += '?, ' if idx != len(data_tuple) else '?'
            
        query = f'INSERT INTO {self.table_name} VALUES({q})'
        
        self.cursor.execute(query, data_tuple)
        self.conn.commit()
        
    
    def backup_table(self):
        
        now = datetime.now()
        with self.conn:
            with open(f'{DB_PATH}/{self.db_name}.sql', 'w') as f:
                
                for line in self.conn.iterdump(): f.write('%s\n' % line)
                print(f'[INFO] [{now}] 테이블 <{self.table_name}> 백업이 완료되었습니다. ')


def save_db(idx, jsons):
    s = time.time()

    for json_path in tqdm(jsons):
        
        now = datetime.now()
        try:
            json_data = load_json(json_path)
            appid, name, gtype = json_data['steam_appid'], json_data['name'], json_data['type']
            DB.insert_table([appid, name, gtype, json.dumps(json_data)])
            
        except Exception as e: print(f'[ERR.DB.I-0001] : [{now}] {e}\n')

    now = datetime.now()
    print(f'[INFO] : [{now}] {idx} DB 저장 완료 ({time.time() - s:,.3f}s)')


json_paths = sorted(list_files(JSON_PATH))
DB = _DB(DB_NAME, TABLE_NAME, [['appid', 'INTEGER', True], 
                              ['name',  'TEXT', True], 
                              ['type',  'TYPE', True],
                              ['json_data', 'json', True]])

DB.create_table()
print(f'[INFO] : [{datetime.now()}]테이블 <{TABLE_NAME}> 생성 완료')

_1st_jobs = json_paths[:len(json_paths) // 4]
_2nd_jobs = json_paths[len(json_paths) // 4 : len(json_paths) // 2]
_3rd_jobs = json_paths[len(json_paths) // 2 : 3 * len(json_paths) // 4]
_4th_jobs = json_paths[3 * len(json_paths) // 4 :]

jobs = [_1st_jobs, _2nd_jobs, _3rd_jobs, _4th_jobs]
start = time.time()
procs = []




for idx, job in enumerate(jobs, 1):
    p = Process(target = save_db, args = (idx, job))
    p.start()
    procs.append(p)
    
for p in procs: p.join()

now = datetime.now()
f'[Done] : [{now}] 수행 시간 : {time.time() - start:,.4f}초'

DB.backup_table()
DB.conn.close()