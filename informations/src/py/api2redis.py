from multiprocessing import Pool, Process
import logging
import time
import json
import os

from easydict import EasyDict as edict
import requests as req
from tqdm import tqdm
import schedule
import redis

def get_logger():

    logger = logging.getLogger('DoveNest')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('\n[%(asctime)s][%(levelname)s] %(name)s : %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    return logger


LOGGER = get_logger()
ROOT_PATH   = '/config/workspace/project'
CONFIG_PATH = f'{ROOT_PATH}/utils/configs/config.json'
PORTS_PATH  = f'{ROOT_PATH}/utils/configs/ports.json'

CONFIG      = edict(json.loads(open(CONFIG_PATH, 'r').read()))
PORTS       = edict(json.loads(open(PORTS_PATH, 'r').read()))
URLS        = {'appdetail' : 'https://store.steampowered.com/api/appdetails?appids' }

HOST        = CONFIG.global_host
PORT        = PORTS.redis_port
conn        = redis.Redis(host = HOST, port = PORT, db = 1, decode_responses = True)

def return_or_print(url):
    
    res = req.get(url)
    if res.status_code == 200: return res.json()
    else: LOGGER.warning(f'no response with code {res.status_code}')
    
    
def get_info(appid):
    
    res = return_or_print(f"https://store.steampowered.com/api/appdetails?appids={appid}&l=korean")
    return res


def save_redis(idx, apps):
 
    for app in tqdm(apps):
        
        appid  = app['appid']
        try:
            info = get_info(appid)[str(appid)]['data']
            data = {
                        'name' : info['name'],
                        'data' : info 
                    }
            
            LOGGER.info('저장중...')
            conn.set(f'id:{appid}', json.dumps(data))
            
        except Exception as e: 
            LOGGER.error(f'[K.1] {e}')

            try:
                data = {'name' : app['name']}
                conn.set(f'id:{appid}', json.dumps(data))

            
            except: LOGGER.error(f'[K.2] {e}')
        
        finally: 
            time.sleep(7)
            
        print(f'[Done] process : {idx}th job is finished.\n')


def begin_jobs():

    apps      = return_or_print('https://api.steampowered.com/ISteamApps/GetAppList/v2')['applist']['apps']
    print(f'original length : {len(apps)}')

    keys      = set(conn.keys())
    condition = lambda x: (f'id:{x["appid"]}' not in keys, x['name'] != '', x['name'].lower() not in 'demo')
    apps      = [app for app in apps if all(condition(app))]

    print(f'작업해야하는 length : {len(apps)}')
    # begin_jobs(apps)
    
    job1 = apps[: len(apps) // 4]
    job2 = apps[len(apps) // 4: len(apps) // 2]
    job3 = apps[len(apps) // 2: 3 * len(apps) // 4]
    job4 = apps[3 * len(apps) // 4 : ]

    jobs  = [job1, job2, job3, job4]
    stime = time.time()
    procs = []
    for idx, job in enumerate(jobs, 1):
        
        p = Process(target = save_redis, args = (idx, job))
        p.start()
        procs.append(p)
        
    for p in procs: p.join()

    time.time() - stime


schedule.every().day.at("09:30").do(begin_jobs)
while True:
    schedule.run_pending()
    time.sleep(1)