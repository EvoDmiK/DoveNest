from multiprocessing import Pool, Process
import logging
import time
import json
import os

from easydict import EasyDict as edict
import requests as req
from tqdm import tqdm
import redis

def get_logger():

    logger = logging.getLogger('DoveNest')
    logger.setLevel(logging.INFO)

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

def return_or_print(url):
    
    res = req.get(url)
    if res.status_code == 200: return res.json()
    else: LOGGER.warning(f'no response with code {res.status_code}')
    
    
def get_info(appid):
    
    res = return_or_print(f"https://store.steampowered.com/api/appdetails?appids={appid}&l=korean")
    return res

key         = CONFIG.steam
host        = CONFIG.global_host
port        = PORTS.redis_port
conn        = redis.StrictRedis(host = host, port = port, db = 1)

apps = return_or_print('https://api.steampowered.com/ISteamApps/GetAppList/v2')['applist']['apps']

print(f'original length : {len(apps)}')
keys = [key.decode().split(':')[1] for key in conn.keys()]
apps = [app['appid'] for app in apps if str(app['appid']) not in keys]
print(f'작업해야하는 length : {len(apps)}')

def save_redis(idx, apps):
 
    for app in tqdm(apps):
        
        try:
            info = get_info(app)[str(app)]['data']
            data = {
                        'name' : info['name'],
                        'data' : info 
                    }
            
            conn.set(f'id:{app}', json.dumps(data))
        except Exception as e: LOGGER.error(e)
        
        finally: 
            time.sleep(5)
            
        print(f'[Done] process : {idx}th job is finished.\n')
            
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