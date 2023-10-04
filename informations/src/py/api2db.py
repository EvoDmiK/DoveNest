from multiprocessing import Pool, Process
from traceback import format_exc
from typing import Union
import logging
import time
import json
import os
import re

from easydict import EasyDict as edict
import requests as req
from tqdm import tqdm
import schedule

from misc.logger import get_logger
from misc.DataBase import _DB


## api 서버에 요청해 데이터를 가져오거나 로깅해주는 함수
def return_or_logging(url: string) -> Union[dict, None]:
    res = req.get(url)
    if res.status_code == 200: return res.json()
    else: LOGGER.warning(f'no response with code {res.status_code}')


## steam api를 이용해서 정보를 가져오는 함수
def get_info(appid: int) -> Union[dict, None]:

    res = return_or_logging(f'{URLS["appdetail"]}={appid}&l=korean')
    return res


## api로 얻은 데이터 DB에 저장해주는 함수
def save_db(idx: int, db: misc.DataBase._DB, apps: list):

    for app in tqdm(apps):

        appid = app['appid']

        try:
            info      = get_info(appid)[str(appid)]['data']
            name      = info['name']
            thumbnail = info['header_image']

            try:    genres = ', '.join(i['description'] for i in info['genres'])
            except: genres = 'N/A'

            try:    developers = ', '.join(info['developers'])
            except: developers = 'N/A'

            try:    publisher  = ', '.join(info['publishers'])
            except: publisher  = 'N/A'

            try:    languages  = info['supported_languages']
            except: languages  = 'N/A'

            ## 무료 게임인 경우에 0원으로 표시하고, 가격 정보가 없는 경우 N/A로 표시
            if info['is_free']: price = '₩ 0'
            else:
                try:    price = info['price_overview']['final_formatted']
                except: price = 'N/A'

            ## 지원 언어에서 필요한 데이터 제거
            for replace in REPLACES: languages = languages.replace(replace, '')
            
            ## 출시 예정작인 경우에 N/A로 표시
            if info['release_date']['coming_soon']: date = 'N/A'
            else: date = info['release_date']['date']

            platforms = info['platforms']
            windows   = platforms['windows']
            linux     = platforms['linux']
            mac       = platforms['mac']

        ## API에서 데이터를 받지 못한 경우 이름, appid를 제외하고 모두 N/A로 표시
        except Exception as e:
            name       = info['name']
            thumbnail  = 'N/A'
            genres     = 'N/A'
            price      = 'N/A'
            developers = 'N/A'
            publisher  = 'N/A'
            windows    =     0
            linux      =     0
            mac        =     0
            languages  = 'N/A'
            date       = 'N/A'
            LOGGER.error(f'[K.2] {e}')

        ## 에러 발생 여부에 상관없이 데이터 DB에 삽입.
        finally:

            db.insert_table([
                    ['appid'    ,      appid],
                    ['title'    ,       name],
                    ['thumbnail',  thumbnail],
                    ['genre'    ,     genres],
                    ['price'    ,      price],
                    ['developer', developers],
                    ['publisher',  publisher],
                    ['windows'  ,    windows],
                    ['linux'    ,      linux],
                    ['mac'      ,        mac],
                    ['languages',  languages],
                    ['date'     ,       date]
                ])

            ## 너무 빨리 요청하면 api에서 접근거부가 발생해 7초 동안 쉬어준 후 다음 작업.
            #! 더 짧게도 해봤는데 7초가 가장 안정적이었음.
            time.sleep(7)

    LOGGER.info(f'[Done] process : {idx}th job is finished. \n')

    
## 데이터 받아오고 분배해주는 함수
def begin_jobs():
    ## DoveNest DB, steam_info 테이블 접속
    db        = _DB(db = 'DoveNest', table = 'steam_info')

    ## api서버에서 받아온 appid 목록
    apps      = return_or_logging(URLS['applists'])['applist']['apps']
    print(f'원래 길이 : {len(apps)}')

    ## DB에 저장되어 있는 appid 집합
    appids    = set([appid[0] for appid in db.select_table(column = 'appid')])

    ## DB에 저장되어 있지 않거나, 이름 정보가 없거나, 데모인 데이터 제외하고 저장 시키기
    condition = lambda x: (x['appid'] not in appids, x['name'] != '', x['name'].lower() not in 'demo')
    apps      = [app for app in apps if all(condition(app))]
    print(f'작업해야 하는 길이 : {len(apps)}')

    ## BATCH SIZE 만큼 작업 BATCH 나눠줌.
    ## 1번째 작업 : [0 : length // BATCH_SIZE]
    ## 2번째 작업 : [length // BATCH_SIZE : (length * 2) // BATCH_SIZE]
    ## ...
    ## n번째 작업 : [(length * (n - 1)) // BATCH_SIZE : (length * n) // BATCH_SIZE]
    jobs = [apps[(idx * len(apps)) // BATCH_SIZE : ((idx + 1) * len(apps)) // BATCH_SIZE]
            for idx in range(BATCH_SIZE)]

    stime = time.time()
    procs = []

    ## 프로세스 별로 작업을 나눠주는 부분
    for idx, job in enumerate(jobs, 1):
        
        ## target은 실행하고자 하는 함수, args는 함수에 들어가는 인자값
        p = Process(target = save_db, args = (idx, db, job))
        p.start()
        procs.append(p)

    for p in procs: p.join()
    time.time() - stime

    ## 프로세스들이 DB에 데이터 저장 작업 마친 후 DB commit
    db.commit()

SEP        = os.path.sep
BATCH_SIZE = 4
ROOT_PATH  = SEP.join(os.getcwd().split(SEP)[:-4])

## supported language에서 필요없어서 제거할 데이터
REPLACES   = ['<br>', '<strong>*</strong>', '음성이 지원되는 언어']
LOGGER     = get_logger()

## 데이터를 가져올 api 서버 URL
## appdetail : appid의 상세 정보를 받아올 수 있는 api 서버
## applist   : steam에 있는 app 데이터들을 받아올 수 있는 api 서버
URLS       = {'appdetail' : 'https://store.steampowered.com/api/appdetails?appids',
              'applists'  : 'https://api.steampowered.com/ISteamApps/GetAppList/v2'}

# begin_jobs()

## 매일 오전 9시 30분에 실행되도록 설정하는 부분
schedule.every().day.at("09:30").do(begin_jobs)
while True:

    schedule.run_pending()
    time.sleep(1)