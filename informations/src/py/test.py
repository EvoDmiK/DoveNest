from datetime import datetime
import sqlite3 as sql
import os

ROOT_PATH = f'/config/workspace/project/DoveNest/informations'
DB_PATH   = f'{ROOT_PATH}/db'

DB_NAME    = 'sale_informations'
TABLE_NAME = 'discounts'

os.makedirs(f'{DB_PATH}', exist_ok = True)

now     = datetime.now()
Y, M, D = now.year, now.month, now.day
today   = f'{Y}{str(M).zfill(2)}{str(D).zfill(2)}'

conn   = sql.connect(f'{DB_PATH}/{DB_NAME}.db')
cursor = conn.cursor()


q = f'select * from discounts where date={today}'
query = cursor.execute(q).fetchall()
print(query, today)