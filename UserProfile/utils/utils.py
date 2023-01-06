from collections import Counter
from datetime import datetime
import traceback
import math as mt
import requests
import os, re
import time
import json

ROOT_PATH  = '/config/workspace/project'

## 미리 API를 통해 받아둔 게임 정보 JSON파일 경로
DATA_PATH  = f'{ROOT_PATH}/DoveNest/steam/jsons'

## youtube, steam API key를 저장하고 있는 경로
JSON_PATH        = f'{ROOT_PATH}/utils/keys'
JSON_BACKUP_PATH = f'{ROOT_PATH}/BACKUPS/keys'

## api URL들을 저장해주는 딕셔너리
URLS = {
    'library'    : 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001',
    'get_summary' : 'https://partner.steam-api.com/ISteamUser/GetPlayerSummaries/v2/',
}


## 유닉스 포맷의 시간 데이터를 파이썬의 datetime 포맷으로 변경시켜주는 함수
unix2datetime = lambda unixtime: str(datetime.fromtimestamp(unixtime))

## json 파일을 불러와주는 함수
load_json     = lambda json_path: json.loads(open(json_path, 'r').read())

## json 파일을 저장하는 함수
save_json     = lambda data, json_path: json.dump(data, open(json_path, 'w'))

## api url을 입력하여 호출해주는 함수
get_api       = lambda url: return_or_print(requests.get(url))


## key를 담고 있는 json 파일이 깨지거나 한 경우에 복구시켜 주는 함수
def repair_keys(json_path):
    try: keys = load_json(f'{json_path}/keys.json')
        
    except Exception as e:
        print(f'[ERR.K.A-001] json 파일이 깨져 열 수 없습니다. {e}')
        text = open(f'{JSON_BACKUP_PATH}/keys.txt', 'r').read().split('\n')
        keys = {platform : key 
                for platform, key in zip(['youtube', 'steam'], text)}
        
        save_paths = [JSON_PATH, JSON_BACKUP_PATH]
        
        print(save_paths)
        for save_path in save_paths:
            
            print(save_path)
            os.makedirs(save_path, exist_ok = True)
            save_json(keys, f'{save_path}/keys.json')
        
    finally: return keys


## steam API 키 가져오는 함수
def get_key():
    if os.path.isfile(f'{JSON_PATH}/keys.json'):
        key = repair_keys(JSON_PATH)['steam']
            
    else:
        print(f'[WARN.K.A-001] json 파일이 존재하지 않아 백업 데이터를 로딩합니다.')
        key = repair_keys(JSON_BACKUP_PATH)['steam']  
    
    return key


## api서버에 request 날렸을 때 정상적으로 돌아오면 데이터,
## 그 외의 경우에는 에러코드 남기는 함수
def return_or_print(response):
    
    if response.status_code == 200: return response.json()
    else: print(f'no response data with code : {response.status_code}')
  

#! 게임 정보를 불러와 주는 api 함수 appid (상점에 있는 내용)을 기반으로 데이터를 불러옴.
## 원래 api를 호출하여 사용하려고 했으나, 한 번 호출하는데 0.3 ~ 0.6초 가량 걸리고,
## 하루 API 허가 호출량이 정해져있어 미리 api로 호출하여 저장해둔 json 데이터를 불러와 사용하는 것으로 변경
def get_info(appid):
    
    json_path = f'{DATA_PATH}/{appid}/{appid}.json'

    if os.path.isfile(json_path): 
        return load_json(json_path)
    
    else:
        print(f'[ERR-J0001] <{appid}> json 파일이 존재하지 않습니다.')
        return {}


## api key와 steam user_id64를 입력받아서 해당 유저의 라이브러리 정보를 불러오는 함수
def get_user_library(key, user_id):
    
    library_url = f'{URLS["library"]}/?key={key}&steamid={user_id}&format=json'
    games = get_api(library_url)['response']['games']
    
    user_datas = []
    for game in games:
        try:
            last_play_time = unix2datetime(game['rtime_last_played'])
            
            info = [game['appid'], game['playtime_forever'], str(last_play_time)]
            user_datas.append(info)
            
        except Exception as e:
            print(traceback.format_exc(), e)
            
    return user_datas


## 가장 많이 플레이한 게임 리스트 5개 반환해주는 함수
def most_played(library, platform = 'steam'):

    library = sorted(library, key = lambda x: x[1], reverse = True)[:5]
    information = []

    for lib in library:
        appid, played_time, last_played = lib
        
        try:
            datas       = load_json(f'{DATA_PATH}/{appid}/{appid}.json')
            played_time = f'{mt.ceil(played_time / 60)} 시간' if played_time / 60 > 1 else f'{int(played_time)} 분'

            info  = {   
                        'image' : datas['header_image'],
                        'name'  : datas['name'],
                        'genre' : ", ".join([data['description'] for data in datas['genres']]),
                        'played_time' : played_time,
                        'last_played' : last_played
                    }
            
            information.append(info)

        except:
            pass 
            # print(f'[WARN.K.L-001] <{appid}> 현재 그 게임은 {platform}에서 제공 되지 않습니다.')

    return information


## 게임 관련 통계 만들어주는 함수
def get_stats(library, platform = 'steam'):
    
    genres, developers = [], []
    num_games = 0

    for lib in library:
        appid, _, _ = lib
        
        try:
            datas = load_json(f'{DATA_PATH}/{appid}/{appid}.json')
            genres     += [data['description'] for data in datas['genres']]
            developers += [data  for  data  in datas['developers']]

            num_games += 1
        except Exception as e:
            pass
            # print(f'[WARN.K.L-001] <{appid}> 현재 그 게임은 {platform}에서 제공 되지 않습니다. {e}')

    genres, developers = Counter(genres), Counter(developers)
    return genres, developers, num_games