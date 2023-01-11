from collections import Counter
from datetime import datetime
import numpy as np
import math as mt
import traceback
import requests
import sqlite3
import os, re
import time
import json

## 모든 경로의 뿌리가 되는 경로
ROOT_PATH  = '/config/workspace/project'

## 미리 API를 통해 받아둔 게임 정보 JSON파일 경로
DATA_PATH  = f'{ROOT_PATH}/DoveNest/informations/jsons'

## 게임 정보들을 모아둔 DB 경로
DB_PATH     = f'{ROOT_PATH}/DoveNest/informations/db'

## youtube, steam 등 API key를 저장하고 있는 경로
JSON_PATH        = f'{ROOT_PATH}/utils/keys'
JSON_BACKUP_PATH = f'{ROOT_PATH}/BACKUPS/keys'

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
    
    ## json 파일이 깨졌을 경우에 백업폴더에 같이 저장되어 있는
    ## 텍스트 파일을 불러와서 복구 시켜주는 부분
    except Exception as e:
        print(f'[ERR.K.A-0001] json 파일이 깨져 열 수 없습니다. {e}')
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
        print(f'[WARN.K.A-0001] json 파일이 존재하지 않아 백업 데이터를 로딩합니다.')
        key = repair_keys(JSON_BACKUP_PATH)['steam']  
    
    return key


## api서버에 request 날렸을 때 정상적으로 돌아오면 데이터,
## 그 외의 경우에는 에러코드 남기는 함수
def return_or_print(response):
    
    if response.status_code == 200: return response.json()
    else: print(f'[ERR.R-001]no response data with code : {response.status_code}')
  

## steam API 관련 클래스 생성
class SteamAPI:
    
    ## api URL들을 저장해주는 딕셔너리
    URLS = {
        'sales'       : 'http://store.steampowered.com/api/featuredcategories/?l=koreana',
        'library'     : 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001',
        'get_summary' : 'https://partner.steam-api.com/ISteamUser/GetPlayerSummaries/v2/',
    }


    #! 게임 정보를 불러와 주는 api 함수 appid (상점에 있는 내용)을 기반으로 데이터를 불러옴.
    ## 원래 api를 호출하여 사용하려고 했으나, 한 번 호출하는데 0.3 ~ 0.6초 가량 걸리고,
    ## 하루 API 허가 호출량이 정해져있어 미리 api로 호출하여 저장해둔 json 데이터를 불러와 사용하는 것으로 변경
    def get_info(appid):
        
        json_path = f'{DATA_PATH}/{appid}/{appid}.json'

        if os.path.isfile(json_path): 
            return load_json(json_path)
        
        else:
            print(f'[ERR.J-0001] <{appid}> json 파일이 존재하지 않습니다.')
            return {}


    ## api key와 steam user_id64를 입력받아서 해당 유저의 라이브러리 정보를 불러오는 함수
    def get_user_library(key, user_id):
        
        library_url = f'{SteamAPI.URLS["library"]}/?key={key}&steamid={user_id}&format=json'
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
                            'genre' : ', '.join([data['description'] for data in datas['genres']][:3]),
                            'played_time' : played_time,
                            'last_played' : last_played
                        }
                
                information.append(info)

            except:
                pass 
                # print(f'[WARN.D.A-0001] <{appid}> 현재 그 게임은 {platform}에서 제공 되지 않습니다.')

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
                # print(f'[WARN.D.A-0001] <{appid}> 현재 그 게임은 {platform}에서 제공 되지 않습니다. {e}')

        genres, developers = Counter(genres), Counter(developers)
        return genres, developers, num_games


    ## 현재 스팀에서 가장 인기 있는 게임들
    def top_sellers(platform = 'steam'):
        sales = get_api(SteamAPI.URLS['sales'])

        top_sellers, top_names = [], []
        for game in sales['top_sellers']['items'][:3]:

            appid = game['id']
            name  = game['name']

            try:
                datas     = get_info(appid)
                genre     = ', '.join([data['description'] for data in datas['genres']][:3])

            
            except Exception as e:
                genre     = f'{platform}에서 제공하지 않음.'
                print(f'[WARN.D.A-0001] <{appid}> 현재 그 게임은 {platform}에서 제공 되지 않습니다. {e}')

        
            info  = {   
                        'image'  : game['header_image'],
                        'name'       : name,
                        'genre'      : genre,
                        'discounted' : game['discounted'],
                    }

            if name not in top_names:
                top_sellers.append(info)
                top_names.append(name)

            else:
                print(f'[WARN.D-0001] 중복된 데이터 입니다. {name}')

        return top_sellers


## 할인 DB 관련 클래스 생성
class salesDB:

    def __init__(self, table_name, db_name):

        self.table_name = table_name
        self.db_name    = db_name
        
        ## DataBase 연결
        self.connect_db()


    ## DB와 연결시켜주는 함수
    def connect_db(self):

        dbpath = f'{DB_PATH}/{self.db_name}.db'
        self.conn   = sqlite3.connect(dbpath, check_same_thread = False)
        self.cursor = self.conn.cursor()


    ## DB에 있는 데이터를 조회하는 함수 고급 쿼리 부분은 좀 더 구현해야 한다.
    def search_table(self, columns = '*', **kwargs):

        ## keyword argument 값에서 데이터가 없는 경우 기본값 지정

        ## 이부분도 너무 킹받게 짜졌다,, 안되는거 그냥 덕지덕지 수정했더니...
        sorting_col = kwargs['sorting_col'] if 'sorting_col' in kwargs.keys() else columns
        sorting_col = sorting_col if sorting_col != '*' else  \
                    ('appid' if type(sorting_col) != list else sorting_col[0])

        conditions  = kwargs['conditions']  if 'conditions' in kwargs.keys() else None
        how_many    = kwargs['how_many']    if 'how_many' in kwargs.keys() else 1
        reverse     = kwargs['desc']        if 'desc' in kwargs.keys() else False

        
        col_indexes = {k : v for v, k in enumerate(['id', 'appid', 'percent', 'original', 
                                                    'discounted', 'date'])}

        ## 코드가 너무 킹받게 짜졌다..
        col_indexes = col_indexes if columns == '*' else \
                    ({k : v for v, k in enumerate(columns)} \
                    if type(columns) == list else {columns : 0})

        col_keys = [col for col in col_indexes.keys()]
        try:
            print(sorting_col, col_keys)
            assert sorting_col in col_keys, f'''\n[ERR.DB.Co-0001] 선택하신 조건에 맞는 컬럼이 존재하지 않아 선택 하신 옵션으로 정렬 할 수 없었습니다. \
                                                {col_keys}에서 골라 주십시오.'''

            columns = ', '.join(columns) if type(columns) == list else columns


            ## 데이터 조회할 때 그 어떤 조건도 없는 경우 그냥 테이블에서 컬럼만 받아 사용
            if conditions == None:
                query = f"""
                            SELECT {columns} FROM {self.table_name}
                        """
            
            else:
                ## 고급 쿼리에 사용할 거
                conditions = np.array(conditions)

                ## WHERE 문으로 찾을 column, 조건, 데이터를 받아 조회해준다.
                if len(conditions) == 3:
                    col, cond, data = conditions

                    symbols = ['>', '<', '!=', '=', '>=', '<=', 'IN']
                    assert cond in symbols, f'\n[ERR.DB.Co-0002] 조건이 올바르지 않습니다. {symbols}에서 선택해 넣어주십시오.'
            
                    
                    query = f"""
                                SELECT {columns} FROM {self.table_name}
                                WHERE {col} {cond} {data};
                            """
                
                ## 데이터를 찾을 column과 찾을 data만 있는 경우
                ## 기본값으로 동일한 데이터만 찾도록 지정해주었다.
                elif len(conditions) == 2:
                    col, data = conditions
                    query = f"""
                                SELECT {columns} FROM {self.table_name}
                                WHERE {col}={data};
                            """

            self.cursor.execute(query)
            
            ## 데이터 정렬에 사용할 인덱스 값들.
            col_index = col_indexes[sorting_col]

        except Exception as e:
            print(f'[ERR.DB.Q-0001] 쿼리에 문제가 발생하였습니다. 확인 후 수정바랍니다. {e}')
            query     = f'SELECT * FROM {self.table_name}'
            col_index = 0

        ## how_many가 0을 포함한 음의 정수가 된다면 모든 데이터를 조회해준다.
        return sorted(self.cursor.fetchmany(how_many), 
                      key = lambda x: x[col_index], reverse = reverse) 


if __name__ == '__main__':
    DB     = salesDB(table_name = 'saleinfo', db_name = 'game_informations')
    result = DB.search_table(columns = ['appid', 'percent', 'discounted'],
                                conditions = ['percent', '<', 5000], how_many = 5)

    print(result)