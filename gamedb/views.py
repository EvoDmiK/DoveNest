from traceback import format_exc
from datetime import datetime
from time import time

from django.core.paginator import Paginator
from django.shortcuts import render

from misc import utils

## mariaDB 연결
DB         = utils.DiscountDB(db_name = 'DoveNest')

## 조회할 CONTENTS 개수
N_CONTENTS = 200

review_dict = { 
                'Overwhelmingly Positive' : '압도적으로 긍정적',
                'Very Positive'           : '매우 긍정적',
                'Positive'                : '긍정적',
                'Mostly Positive'         : '대체로 긍정적',
                'Mixed'                   : '복합적',
                'Mostly Negative'         : '대체로 부정적',
                'Negative'                : '부정적',
                'Very Negative'           : '매우 부정적',
                'Overwhelmingly Negative' : '압도적으로 부정적'
            }

## 게임 할인 정보 페이지에 표시되는 데이터 로딩하는 함수.
def gamedb(request):
    NOW  = datetime.now()
    Y,M,D = NOW.year, NOW.month, NOW.day

    datas = []
    today =  f'{Y}{str(M).zfill(2)}{str(D).zfill(2)}'

    ## html에서 GET으로 데이터를 받았을 때 정렬 기준 설정
    if request.method == 'GET': 
        sorting_ = showing = request.GET.get('sorting_')
        sorting_ = sorting_ if sorting_ != None else 'idx'
        showing  = showing  if sorting_ != None else '인기순'

    else:
        sorting_, showing = 'idx', '정렬 기준'

    ## percent, name의 경우 내림차순으로 정렬, 그 외의 경우에는 오름차순으로 정렬.
    if sorting_ == 'percent': desc = 'percent desc'
    else: desc = f'{sorting_} asc'

    ## DB에서 데이터 가져오는 부분
    print(today)
    db_datas   = DB.select_db('discount_info', order = desc, limit_k = N_CONTENTS,
                               cond = f'(date = {today}) and (platform = "steam") and (not review is null)')
    
    ## 조회한 쿼리셋에서 데이터 처리 해주는 부분.
    for db_data in db_datas:

        ## 고유 번호, 게임 이름, 할인율, 할인가, 원본가, 게임 플랫폼, 게임 페이지, 썸네일, 날짜, 리뷰
        _, appid, name, percent, discounted, original, platform, page, thumbnail, _, review = db_data
        

        ## db에서 가져온 데이터의 게임 장르 중 3개 가져오기
        genre     = utils.SteamAPI.get_genre(appid, platform)

        discounted = discounted.strip()
        original   = original.strip()

        review = ' '.join(review.split()[:1 if 'mixed' in review.lower() else 2])

        try:
            info = {
                    'image'      : thumbnail,
                    'name'       : name,
                    'genre'      : genre,
                    'original'   : original,
                    'percentage' : f'-{percent}%',
                    'discounted' : discounted, 
                    'steam_page' : page,
                    'review'     : review_dict[review]
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



