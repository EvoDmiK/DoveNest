from traceback import format_exc
import json
import os
import re

from easydict import EasyDict as edict
import requests as req
import pymysql as sql
from tqdm import tqdm
import redis

from misc.DataBase import _DB

SEP       = os.path.sep
ROOT_PATH = SEP.join(os.getcwd().split(SEP)[:-4])
JSON_PATH = f'{ROOT_PATH}/utils/configs'
print(ROOT_PATH)

read_json = lambda path: edict(json.loads(open(path, 'r').read()))
REPLACES  = ['<br>', '<strong>*</strong>', '음성이 지원되는 언어']
CONFIGS   = read_json(f'{JSON_PATH}/config.json')
PORTS     = read_json(f'{JSON_PATH}/ports.json')
URLS      = {'appdetail' : 'https://store.steampowered.com/api/appdetails?appids'}

CONFIGS   = edict(CONFIGS)
PORTS     = edict(PORTS)
DB        = _DB(db = 'DoveNest', table = 'steam_info')

rport  = PORTS.redis_port
host   = CONFIGS.global_host
rconn  = redis.StrictRedis(host = host, port = rport, db = 1)
datas  = rconn.keys('*')

for data in tqdm(datas):

    appid = data.decode().replace('id:', '')
    try:
        data      = json.loads(rconn.get(data))
        data      = data['data']
        name      = data['name']
        appid     = data['steam_appid']
        thumbnail = data['header_image']

        name = name.replace('"', '')
        try: genres    = ', '.join(d['description'] for d in data['genres'])
        except: genres = 'N/A'
        
        if data['is_free']: price = '₩ 0'
        else: 
            try: price = data['price_overview']['final_formatted']
            except: price = 'N/A'

        try: developers = ', '.join(data['developers'])
        except: developers = 'N/A'

        try: publishers = ', '.join(data['publishers'])
        except: publishers = 'N/A'

        try: languages  = data['supported_languages']
        except: languages = 'N/A'
        
        for replace in REPLACES: languages = languages.replace(replace, '')
        platforms  = data['platforms']

        if data['release_date']['coming_soon']: date = 'N/A'
        else: date = data['release_date']['date']

        windows = platforms['windows']
        linux   = platforms['linux']
        mac     = platforms['mac']

    except Exception as e:

        name       = data['name']
        thumbnail  = 'N/A'
        genres     = 'N/A'
        price      = 'N/A'
        developers = 'N/A'
        publishers = 'N/A'
        platforms  = 'N/A'
        languages  = 'N/A'
        windows    = 0
        linux      = 0
        mac        = 0
        date       = 'N/A'

    finally:

        DB.insert_table([
            ['appid'    ,      appid],
            ['title'    ,       name],
            ['thumbnail',  thumbnail],
            ['genre'    ,     genres],
            ['price'    ,      price],
            ['developer', developers],
            ['publisher', publishers],
            ['windows'  ,    windows],
            ['linux'    ,      linux],
            ['mac'      ,        mac], 
            ['languages',  languages],
            ['date'     ,       date]
        ])

DB.commit()