from django.core.paginator import Paginator
from django.shortcuts import render
from datetime import datetime
from UTILS import utils
from time import time

DB = utils.salesDB(table_name = 'saleinfo', db_name = 'game_informations')
def gamedb(request):
    NOW  = datetime.now()
    Y,M,D = NOW.year, NOW.month, NOW.day

    datas    = []
    db_datas = DB.search_table(how_many = 100)

    for db_data in db_datas:
        _, appid, percent, original, discounted, platform, _ = db_data
        
        json_data = utils.SteamAPI.get_info(appid)
        genre = utils.SteamAPI.get_genre(appid, platform, datas = json_data)

        info = {
                'image'      : json_data['header_image'],
                'name'       : json_data['name'],
                'genre'      : genre,
                'original'   : f'₩ {original:,}',
                'percentage' : f'-{percent}%',
                'discounted' : f'₩ {discounted:,}', 
            }

        datas.append(info)

    ## 페이지 네이션 해주는 부분
    page = request.GET.get('page', '1')

    ## 한 페이지에 20개의 할인 정보씩 보여지도록 구성
    paginator = Paginator(datas, 20)
    page_obj  = paginator.get_page(page)

    context = {'datas' : page_obj}
    return render(request, 'sales.html', context = context)



