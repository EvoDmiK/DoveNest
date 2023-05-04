from traceback import format_exc
import json
import os

from easydict import EasyDict as edict

from misc import logger

ROOT_PATH        = '/config/workspace/project'
DATA_PATH        = f'{ROOT_PATH}/DoveNest/informations/jsons'

JSON_PATH        = f'{ROOT_PATH}/utils/configs'
JSON_BACKUP_PATH = f'{ROOT_PATH}/BACKUPS/configs'

DB_PATH          = f'{ROOT_PATH}/DoveNest/informations/db'
CONFIG_NAMES     = [  'port',   'host',  'passwd', 'api_host',
                    'youtube',  'steam', 'openai',
                    'mrcon_api_int_port',
                    'mrcon_api_ext_port',
                    'chimhaha_int_port', 
                    'chimwiki_int_port', 
                    'dovenest_int_port', 
                    'dovenest_api_int_port']

LOGGER        = logger.get_logger()

## json 파일을 불러와주는 함수
load_json     = lambda json_path: json.loads(open(json_path, 'r').read())

## json 파일을 저장하는 함수
save_json     = lambda data, json_path: json.dump(data, open(json_path, 'w'), indent = 2)

## key를 담고 있는 json 파일이 깨지거나 한 경우에 복구시켜 주는 함수
def repair_json(json_path: str, ftype: str = 'config') -> dict:
    ## == 입력 값 ==
    ## json_path : config 파일이 저장되어 있는 경로

    ## == 출력 값 ==
    ## config 파일에 저장되어 있는 세팅 값들.
    
    try: config = load_json(f'{json_path}/{ftype}.json')
    
    ## json 파일이 깨졌을 경우에 백업폴더에 같이 저장되어 있는
    ## 텍스트 파일을 불러와서 복구 시켜주는 부분
    except Exception as e:
        LOGGER.error(f'[ERR.K.A-0001] json 파일이 깨져 열 수 없습니다. {e} \n{format_exc()}')
        texts  = open(f'{JSON_BACKUP_PATH}/{ftype}.txt', 'r').readlines()
        
        texts  = [text.split() for text in texts]
        json_  = {name : text  for name, text in texts}
        
        save_paths = [JSON_PATH, JSON_BACKUP_PATH]
        
        for save_path in save_paths:
            
            os.makedirs(save_path, exist_ok = True)
            save_json(json_, f'{save_path}/{ftype}.json')
        
    finally: return json_


## steam API 키 가져오는 함수
def get_config():

    if os.path.isfile(f'{JSON_PATH}/config.json'):
        config = repair_json(JSON_PATH)

    else:
        LOGGER.warning('[WARN.K.A-0001] json 파일이 존재하지 않아 백업 데이터를 로딩합니다.')
        config = repair_json(JSON_BACKUP_PATH)

    return edict(config)


def get_ports():

    if os.path.isfile(f'{JSON_PATH}/ports.json'):
        ports = repair_json(JSON_PATH, ftype = 'ports')

    else:
        LOGGER.warning('[WARN.K.A-0001] json 파일이 존재하지 않아 백업 데이터를 로딩합니다.')
        ports = repair_json(JSON_BACKUP_PATH, ftype = 'ports')

    return edict(ports)


## api URL들을 저장해주는 딕셔너리
URLS  = {
    'sales'       : 'http://store.steampowered.com/api/featuredcategories/?l=koreana',
    'library'     : 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001',
    'steamspy'    : 'https://steamspy.com/',
    'steam_page'  : 'https://store.steampowered.com/app',
    'get_summary' : 'https://partner.steam-api.com/ISteamUser/GetPlayerSummaries/v2/',
}

CONFIG = get_config()
PORTS  = get_ports()
URLS   = edict(URLS)