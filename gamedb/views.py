from traceback import format_exc
from datetime import datetime
from time import time

from django.core.paginator import Paginator
from django.shortcuts import render

from misc import utils

DB         = utils.SalesDB(table_name = 'discount_info', db_name = 'DoveNest')
N_CONTENTS = 200

def gamedb(request):
    NOW  = datetime.now()
    Y,M,D = NOW.year, NOW.month, NOW.day

    datas = []
    today =  f'{Y}{str(M).zfill(2)}{str(D).zfill(2)}'

    if request.method == 'GET': 
        sorting_ = showing = request.GET.get('sorting_')
        sorting_ = sorting_ if sorting_ != None else 'idx'
        showing  = showing  if sorting_ != None else '인기순'


    desc     = True if sorting_ in ['percent', 'name'] else False
    db_datas = DB.search_table(how_many = N_CONTENTS, conditions = ['date', today], 
                               desc = desc, sorting_col = sorting_)
    for db_data in db_datas:

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
                    'original'   : original,
                    'percentage' : f'-{percent}%',
                    'discounted' : discounted, 
                    'steam_page' : page
                }
            datas.append(info)
        
        except Exception as e:
                print(f'[WARN.D.A-0001] <{appid}> 현재 그 컨텐츠는 {platform}에서 제공 되지 않습니다. {e}')
                print(format_exc())

    ## 페이지 네이션 해주는 부분
    page = request.GET.get('page', '1')

    ## 한 페이지에 20개의 할인 정보씩 보여지도록 구성
    paginator = Paginator(datas, 20)
    page_obj  = paginator.get_page(page)

    context = {
               'datas'     : page_obj,
               'last_page' : int(len(db_datas) // 20),
               'showing'   : showing
            }
    return render(request, 'sales.html', context = context)



