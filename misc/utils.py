from traceback import format_exc
from collections import Counter
from datetime import datetime
import math as mt
import time
import json
import os
import re

from bs4 import BeautifulSoup as bs
from steam import Steam
import requests as req
import pymysql as sql
import numpy as np
# import sqlite3

from misc import configs

LOGGER     = configs.LOGGER
CONFIG     = configs.CONFIG
PORTS      = configs.PORTS

## 모든 경로의 뿌리가 되는 경로
ROOT_PATH  = configs.ROOT_PATH

## 미리 API를 통해 받아둔 게임 정보 JSON파일 경로
DATA_PATH  = configs.DATA_PATH

## 게임 정보들을 모아둔 DB 경로
DB_PATH    = configs.DB_PATH

## 유닉스 포맷의 시간 데이터를 파이썬의 datetime 포맷으로 변경시켜주는 함수
unix2datetime = lambda unixtime: str(datetime.fromtimestamp(unixtime))

## json 파일을 불러와주는 함수
load_json     = lambda json_path: json.loads(open(json_path, 'r').read())

## json 파일을 저장하는 함수
save_json     = lambda data, json_path: json.dump(data, open(json_path, 'w'))

## api url을 입력하여 호출해주는 함수
get_api       = lambda url: return_or_print(req.get(url))


## api서버에 request 날렸을 때 정상적으로 돌아오면 데이터,
## 그 외의 경우에는 에러코드 남기는 함수
def return_or_print(response: req.models.Response) -> dict:
    
    ## == 입력 값 ==
    ## response : API 서버에 요청해서 받은 반환 값

    ## == 출력 값 ==
    ## response 코드가 200인 경우만 웹으로 부터 전달 받은 response 값을 json 형태로 반환

    if response.status_code == 200: return response.json()
    else: LOGGER.error(f'[ERR.R-0001] no response data with code : {response.status_code}')
  

def get_sale_items(n_contents = 10, query = None):

    NOW     = datetime.now()
    Y, M, D = NOW.year, NOW.month, NOW.day

    datas   = {}
    today   = f'{Y}{str(M).zfill(2)}{str(D).zfill(2)}'

    sorting_ = query if query != None else 'idx'
    desc     = True  if sorting_ in ['percent', 'name'] else False
    db_datas = DB.search_table(
                                table_name = 'discount_info', how_many = n_contents, 
                                conditions  = ['date', today], desc     =       desc, 
                                sorting_col = sorting_
                            )

    for idx, db_data in enumerate(db_datas):

        _, appid, name, percent, discounted, original, platform, page, thumbnail, _ = db_data

        json_data = utils.SteamAPI.get_info(appid)
        genre = utils.SteamAPI.get_genre(appid, platform)

        discounted = discounted.strip()
        original   = original.strip()

        try:
            info = {
                    'image'      : thumbnail,
                    'name'       : name,
                    'genre'      : genre,
                    'original'   : f'{original:}',
                    'percentage' : f'-{percent}%',
                    'discounted' : f'{discounted:}', 
                    'steam_page' : page
                }
            datas[idx] = data

        except Exception as e:
                print(f'[WARN.D.A-0001] <{appid}> 현재 그 컨텐츠는 {platform}에서 제공 되지 않습니다. {e}')

    return {"data" : datas}


## steam API 관련 클래스 생성
class SteamAPI:
    
    STEAM = Steam(CONFIG.steam)
    URLS  = configs.URLS

    ## 
    def search_user(user_name: str) -> dict:

        user_info = SteamAPI.STEAM.search_user(user_name)
        if user_info == 'str': 
            avatar = f'{ROOT_PATH}/DoveNest/templates/static/assets/images/avatar-01.jpg'
            return {'steamid' : 'Not Matched', 'personalname' : None, 'avatar' : avatar}
        else:
            avatar       = user_info['player']['avatar']
            steamid      = user_info['player']['steamid']
            personalname = user_info['player']['personaname']

            return {'steamid' : steamid, 'personalname' : personalname, 'avatar' : avatar}


    #! 게임 정보를 불러와 주는 api 함수 appid (상점에 있는 내용)을 기반으로 데이터를 불러옴.
    ## 원래 api를 호출하여 사용하려고 했으나, 한 번 호출하는데 0.3 ~ 0.6초 가량 걸리고,
    ## 하루 API 허가 호출량이 정해져있어 미리 api로 호출하여 저장해둔 json 데이터를 불러와 사용하는 것으로 변경
    def get_info(appid: str) -> dict:
        
        ## == 입력 값 ==
        ## appid : 게임의 고유 id

        ## == 출력 값 ==
        ## json 파일이 있을 경우에는 저장되어 있는 json 파일을 불러와 반환
        ## json 파일이 없는 경우에는 어쩔 수 없이 API로 받아와서 반환 
        json_path = f'{DATA_PATH}/{appid}/{appid}.json'

        if os.path.isfile(json_path): 
            return load_json(json_path)
        
        else:
            print(f'[ERR.J-0001] <{appid}> json 파일이 존재하지 않습니다.')
            
            return {}


    ## api key와 steam user_id64를 입력받아서 해당 유저의 라이브러리 정보를 불러오는 함수
    def get_user_library(key: str, user_id: str) -> list:
        
        ## == 입력 값 ==
        ## key     : 스팀 API키
        ## user_id : 유저의 스팀 id 64

        ## == 출력 값 ==
        ## [게임 고유 id, 지금까지 플레이 한 시간, 마지막 플레이 시간]을 리스트로 묶어 반환
         
        library_url = f'{SteamAPI.URLS["library"]}/?key={key}&steamid={user_id}&format=json'
        games = get_api(library_url)['response']['games']
        
        user_datas = []
        for game in games:
            try:
                last_play_time = unix2datetime(game['rtime_last_played'])
                
                info = [game['appid'], game['playtime_forever'], str(last_play_time)]
                user_datas.append(info)
                
            except Exception as e:
                print(f'{format_exc()}')
                
        return user_datas


    ## 가장 많이 플레이한 게임 리스트 5개 반환해주는 함수
    def most_played(library: list, platform: str = 'steam') -> list:
        
        ## == 입력 값 ==
        ## library  : 유저의 라이브러리 
        ## platform : 게임 플랫폼 (steam, blizzard, riot, epic games, nintendo, ...)

        ## == 출력 값 ==
        ## 게임의 썸네일, 제목, 장르, 플레이 시간, 마지막 플레이 시간으로 
        ## 구성된 딕셔너리 5개가 리스트 형태로 묶여 있는 반환 값
          
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
                # pass 
                LOGGER.warning(f'[WARN.D.A-0001] <{appid}> 현재 그 게임은 {platform}에서 제공되지 않습니다.')

        return information


    ## 게임 관련 통계 만들어주는 함수
    def get_stats(library: list , platform: str = 'steam') -> tuple:
        
        ## == 입력 값 ==
        ## library  : 유저의 라이브러리 
        ## platform : 게임 플랫폼 (steam, blizzard, riot, epic games, nintendo, ...)

        ## == 출력 값 ==
        ## 게임의 장르, 개발사 별 개수와 현재 가지고 있는 게임의 개수를 묶어 반환

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
        return (genres, developers, num_games)


    ## 게임에서 장르 가져와주는 함수
    def get_genre(appid: str, platform: str) -> str:

        ## == 입력 값 ==
        ## appid    : 게임의 고유 아이디
        ## platform : 게임 플랫폼 (steam, blizzard, riot, epic games, nintendo, ...)

        ## == 출력 값 ==
        ## 게임의 장르가 여러 개인 경우 너무 길어져 3개 까지만 묶어 반환

        try:
            datas = SteamAPI.get_info(appid)
            genre = ', '.join([data['description'] for data in datas['genres']][:3])

    
        except Exception as e:
            genre  = f'{platform}에서 제공하지 않음.'
            LOGGER.warning(f'[WARN.D.A-0001] <{appid}> 현재 그 게임은 {platform}에서 제공되지 않습니다. \n')
        return genre


    ## 현재 스팀에서 가장 많이 팔리고 있는 게임들 
    def get_topsellers(sales: dict, platform: str, top_sellers: list, top_names: list, nums: tuple) -> list:
        
        num1, num2 = nums
        for game in sales['top_sellers']['items'][num1 : num2]:

            appid = game['id']
            name  = game['name']

            genre = SteamAPI.get_genre(appid, platform)

            info  = {   
                        'image'      : game['header_image'],
                        'name'       : name,
                        'genre'      : genre,
                        'discounted' : game['discounted'],
                        'steam_page' : f'{SteamAPI.URLS["steam_page"]}/{appid}'
                    }

            if name not in top_names:
                top_sellers.append(info)
                top_names.append(name)

            else:
                LOGGER.warning(f'[WARN.D-0001] 중복된 데이터 입니다. {name}')

        return top_sellers, top_names


    ## 현재 스팀에서 가장 인기 있는 게임들
    def get_trendy(nums = 10):
        
        response = req.get(SteamAPI.URLS['steamspy'])
        if response.status_code == 200:
            
            soup  = bs(response, 'html.parser')

            ## steamspy에서 데이터 있는 테이블 스크래핑 
            datas = list(soup.select('table.table-striped > tbody > tr > td'))

            ## 500개 이후로는 데이터가 깨짐.
            nums  = nums if nums < 500 else 500
            
            ## 필요없는 데이터 제거
            datas = [data for data in datas if 'tplaytime' not in str(data)][:nums]

            ## 한 게임에 대한 데이터가 총 6 라인으로 구성되어 있는데, 
            ## 그 중 유의미한 데이터는 1번째 라인 ~ 5번째 라인까지여서 유의미한 데이터만 묶음.
            datas = [datas[idx + 1 : idx + 5] for idx in range(0, len(datas), 6)]

            for data in datas:

                try:
                    ## title : 게임 제목
                    ## date  : 게임 출시일
                    ## price : 게임 가격 (달러 단위)
                    info, date, price, score = data

                    title = title.text
                    date  = date.text
                    price = price.text

                    ## appid     : 게임의 고유 아이디
                    ## thumbnail : 게임 썸네일
                    try: 
                        appid     = info.select('a')[0]['href'].split('/')[2]
                        thumbnail = info.select('a > img')[0]['src']

                    except: 
                        print('[ERR.D.H.0001] 지정해 주신 태그에서 원하시는 데이터를 찾을 수 없었습니다.')
                        appid     = '000'
                        thumbnail = f'{ROOT_PATH}/DoveNest/templates/static/assets/images/avatar-01.jpg'

                    infos = {
                                'title' : title, 'date'      : date, 'price' : price,
                                'appid' : appid, 'thumbnail' : thumbnail
                            }
                    
                except:
                    print('[ERR.D.H.0001] 지정해 주신 태그에서 원하시는 데이터를 찾을 수 없었습니다.')
                    appid     = '000'
                    thumbnail = f'{ROOT_PATH}/DoveNest/templates/static/assets/images/avatar-01.jpg'

                    infos = {
                                'title' : None,  'date'      : None,     'price' : '$0.00',
                                'appid' : appid, 'thumbnail' : thumbnail
                            }

        else:
            LOGGER.error(f'[ERR.R-0001] no response data with code : {response.status_code}')

        return infos


## 할인 DB 관련 클래스 생성
class SalesDB:

    def __init__(self, db_name):

        self.db_name    = db_name

        self.passwd     = CONFIG.sql_passwd
        self.host       = CONFIG.global_host
        self.user       = CONFIG.sql_user
        self.port       = PORTS.sql_port
        
        ## DataBase 연결
        self.connect_db()


    ## DB와 연결시켜주는 함수
    def connect_db(self):

        # dbpath = f'{DB_PATH}/{self.db_name}.db'
        # self.conn   = sqlite3.connect(dbpath, check_same_thread = False)
        # self.cursor = self.conn.cursor()

        self.conn = sql.connect(host   = self.host, port = self.port, 
                                user = self.user, passwd = self.passwd, db = self.db_name)
        self.cursor = self.conn.cursor()


    ## DB에 있는 데이터를 조회하는 함수 고급 쿼리 부분은 좀 더 구현해야 한다.
    def search_table(self, table_name, columns = '*', platform = 'steam', **kwargs):

        ## keyword argument 값에서 데이터가 없는 경우 기본값 지정
        ## 이부분도 너무 킹받게 짜졌다,, 안되는거 그냥 덕지덕지 수정했더니...
        sorting_col = kwargs['sorting_col'] if 'sorting_col' in kwargs.keys() else columns
        sorting_col = sorting_col if sorting_col != '*' else  \
                    ('appid' if type(sorting_col) != list else sorting_col[0])

        conditions  = kwargs['conditions']  if 'conditions' in kwargs.keys() else None
        how_many    = kwargs['how_many']    if 'how_many' in kwargs.keys() else 1
        reverse     = kwargs['desc']        if 'desc' in kwargs.keys() else False

        
        col_indexes = {k : v for v, k in enumerate(['idx', 'appid', 'name', 'percent', 
                                                    'original', 'discounted', 'date'])}

        ## 코드가 너무 킹받게 짜졌다..
        col_indexes = col_indexes if columns == '*' else \
                    ({k : v for v, k in enumerate(columns)} \
                    if type(columns) == list else {columns : 0})

        col_keys = [col for col in col_indexes.keys()]

        try:
            assert sorting_col in col_keys, f'''\n[ERR.DB.Co-0001] 선택하신 조건에 맞는 컬럼이 존재하지 않아 선택 하신 옵션으로 정렬 할 수 없었습니다. \
                                                {col_keys}에서 골라 주십시오.'''

            columns = ', '.join(columns) if type(columns) == list else columns


            ## 데이터 조회할 때 그 어떤 조건도 없는 경우 그냥 테이블에서 컬럼만 받아 사용
            if conditions == None:
                query = f"""
                            SELECT DISTINCT {columns} FROM {table_name} WHERE platform='{platform}'
                        """
            
            else:
                ## 고급 쿼리에 사용할 거
                conditions = np.array(conditions)

                ## WHERE 문으로 찾을 column, 조건, 데이터를 받아 조회해준다.
                if len(conditions) == 3:
                    col, cond, data = conditions

                    print('\n\n', col, cond, data, '\n\n')
                    symbols = ['>', '<', '!=', '=', '>=', '<=', 'IN']
                    assert cond in symbols, f'\n[ERR.DB.Co-0002] 조건이 올바르지 않습니다. {symbols}에서 선택해 넣어주십시오.'
            
                    
                    query = f"""
                                SELECT DISTINCT {columns} FROM {table_name}
                                WHERE {col} {cond} {data} AND platform='{platform}';
                            """
                
                ## 데이터를 찾을 column과 찾을 data만 있는 경우
                ## 기본값으로 동일한 데이터만 찾도록 지정해주었다.
                elif len(conditions) == 2:
                    col, data = conditions
                    query = f"""
                                SELECT DISTINCT {columns} FROM {table_name}
                                WHERE {col}={data} AND platform='{platform}';
                            """

            self.cursor.execute(query)
            
            ## 데이터 정렬에 사용할 인덱스 값들.
            col_index = col_indexes[sorting_col]

        except Exception as e:
            LOGGER.error(f'[ERR.DB.Q-0001] 쿼리에 문제가 발생하였습니다. 확인 후 수정 바랍니다. \n{format_exc()}')
            query     = f'SELECT * FROM {table_name}'
            col_index = 0

        ## how_many가 0을 포함한 음의 정수가 된다면 모든 데이터를 조회해준다.
        return sorted(self.cursor.fetchmany(how_many), 
                      key = lambda x: x[col_index], reverse = reverse)


DB = SalesDB(db_name = 'DoveNest')