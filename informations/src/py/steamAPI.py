from multiprocessing import Pool, Process
import time
import json
import os
import re

from imutils.paths import list_files
from tqdm import tqdm
import pandas as pd
import requests

ROOT_PATH = '/config/workspace/project/DoveNest'
SAVE_PATH = f'{ROOT_PATH}/informations/jsons'

get_api  = lambda url: return_or_print(requests.get(url))

def return_or_print(response):
    
    if response.status_code == 200: return response.json()
    else: print(f'no response data with code : {response.status_code}')
    

def get_info(appid):
    
    response = requests.get(f'https://store.steampowered.com/api/appdetails?appids={appid}&l=korean')
    return return_or_print(response)
    
    
def get_reviews(appid):
    
    response = requests.get(f'https://store.steampowered.com/appreviews/{appid}?json=1')
    return return_or_print(response)


def get_requirements(info, platform = 'pc', typeof = 'minimum'):
    
    assert platform in ['pc', 'linux', 'mac'], 'platform must be pc, linux and mac'
    assert typeof in ['minimum', 'recommended'], 'type of must be minimum, recommended'
    
    requirements = info[f'{platform}_requirements'][typeof]
    requirements = re.sub('(<([^>]+)>)', '\n', requirements)
    
    requirements = requirements.split('\n')
    requirements = [req for req in requirements if req != '']
    
    result = {}
    for idx in range(1, len(requirements), 2): 
        
        print(requirements[idx: idx + 2])
        key, value = requirements[idx: idx + 2]
        result[key] = value
        
    return result


steam_apps = get_api('https://api.steampowered.com/ISteamApps/GetAppList/v2')['applist']['apps']

jsons = list(list_files(SAVE_PATH))
jsons = set([j.split(os.path.sep)[-2] for j in jsons])
print(len(jsons))

steam_apps = [app['appid'] for app in steam_apps if str(app['appid']) not in jsons]
print(len(steam_apps))

def save_json(idx, apps):

    for app in tqdm(apps):
        
        try:
            json_path = f'{SAVE_PATH}/{app}' 
            
            try:
                info = get_info(app)[str(app)]['data']
                
                os.makedirs(json_path, exist_ok = True)
                f = open(f'{json_path}/{app}.json', 'w', encoding='utf-8')
                json.dump(info, f, ensure_ascii=False,indent = 4)
            
            except Exception as e:
                print(f'[Error. 001] json file can\'t save : [{app}] {e}\n')

            time.sleep(7)

        except Exception as e:
            print(f'[Error. 002] api data receieve failed : [{app}] {e}\n')

    print(f'[Done] process : {idx} done.\n')

_1st_jobs = steam_apps[:len(steam_apps) // 4]
_2nd_jobs = steam_apps[len(steam_apps) // 4 : len(steam_apps) // 2]
_3rd_jobs = steam_apps[len(steam_apps) // 2 : 3 * len(steam_apps) // 4]
_4th_jobs = steam_apps[3 * len(steam_apps) // 4 :]

jobs = [_1st_jobs, _2nd_jobs, _3rd_jobs, _4th_jobs]
start = time.time()
procs = []

for idx, job in enumerate(jobs, 1):
    p = Process(target = save_json, args = (idx, job))
    p.start()
    procs.append(p)
    
for p in procs: p.join()

f'[Done] 수행 시간 : {time.time() - start:.4f}초'
