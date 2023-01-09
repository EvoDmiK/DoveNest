from multiprocessing import Pool, Process
import pandas as pd
import requests
import os, re
import time
import json

def return_or_print(response):
    
    if response.status_code == 200: return response.json()
    else: print(f'no response data with code : {response.status_code}')

    
get_api  = lambda url: return_or_print(requests.get(url))

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


steam_games = get_api('https://api.steampowered.com/ISteamApps/GetAppList/v2')['applist']['apps']

def save_json(idx, games):
    database = {}

    for game in games:
        appid     = game['appid']
        
        try:
            json_path = f'jsons/{appid}' 
            
            try:
                info = get_info(appid)[str(appid)]['data']
                
                os.makedirs(json_path, exist_ok = True)
                f = open(f'{json_path}/{appid}.json', 'w', encoding='utf-8')
                json.dump(info, f, ensure_ascii=False,indent = 4)
            
            except Exception as e:
                print(f'[Error. 001] json file can\'t save : [{appid}] {e}\n')
                
            database['appid']     = appid
            database['json_path'] = f'{json_path}/{appid}.json'

            time.sleep(7)

        except Exception as e:
            print(f'[Error. 002] api data receieve failed : [{appid}] {e}\n')

    print(f'[Done] process : {idx} done.\n')

_1st_jobs = steam_games[:len(steam_games) // 4]
_2nd_jobs = steam_games[len(steam_games) // 4 : len(steam_games) // 2]
_3rd_jobs = steam_games[len(steam_games) // 2 : 3 * len(steam_games) // 4]
_4th_jobs = steam_games[3 * len(steam_games) // 4 :]

jobs = [_1st_jobs, _2nd_jobs, _3rd_jobs, _4th_jobs]
start = time.time()
procs = []

for idx, job in enumerate(jobs, 1):
    p = Process(target = save_json, args = (idx, job))
    p.start()
    procs.append(p)
    
for p in procs: p.join()

f'[Done] 수행 시간 : {time.time() - start:.4f}초'
