from django.core.paginator import Paginator
from django.shortcuts import render
from datetime import datetime
from UTILS import utils
from time import time

DB         = utils.SalesDB(table_name = 'saleinfo', db_name = 'game_informations')
N_CONTENTS = 100

def gamedb(request):
    NOW  = datetime.now()
    Y,M,D = NOW.year, NOW.month, NOW.day

    datas = []
    today =  f'{Y}{str(M).zfill(2)}{str(D).zfill(2)}'

    db_datas = DB.search_table(how_many = 100, conditions = ['date', today], sorting_col = 'id')
    for db_data in db_datas:
        _, appid, percent, original, discounted, platform, _ = db_data
        
        json_data = utils.SteamAPI.get_info(appid)
        genre = utils.SteamAPI.get_genre(appid, platform, datas = json_data)

        try:
            info = {
                    'image'      : json_data['header_image'],
                    'name'       : json_data['name'],
                    'genre'      : genre,
                    'original'   : f'₩ {original:,}',
                    'percentage' : f'-{percent}%',
                    'discounted' : f'₩ {discounted:,}', 
                    'steam_page' : f'{utils.SteamAPI.URLS["steam_page"]}/{appid}'
                }

        except Exception as e:
                print(f'[WARN.D.A-0001] <{appid}> 현재 그 게임은 {platform}에서 제공 되지 않습니다. {e}')

        datas.append(info)

    ## 페이지 네이션 해주는 부분
    page = request.GET.get('page', '1')

    ## 한 페이지에 20개의 할인 정보씩 보여지도록 구성
    paginator = Paginator(datas, 20)
    page_obj  = paginator.get_page(page)

    context = {
               'datas'     : page_obj,
               'last_page' : int(len(db_datas) // 20)
            }
    return render(request, 'sales.html', context = context)



