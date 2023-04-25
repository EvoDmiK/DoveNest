from datetime import datetime

from django.shortcuts import render

from utils import utils
# Create your views here.s

## 현재 스팀에서 가장 인기 있는 게임들
def recent_trendy(platform = 'steam'):

    sales = utils.get_api(utils.SteamAPI.URLS['sales'])
    top_sellers, top_names = utils.SteamAPI.get_topsellers(sales, platform, [], [], [0, 3])

    ## 중복 데이터 때문에 표시되는 데이터가 3개보다 적은 경우 처리
    if len(top_sellers) != 3:
        top_sellers, _ = utils.SteamAPI.get_topsellers(sales, platform, top_sellers,
                                                       top_names, [3, 6 - len(top_sellers)])

    return top_sellers


def home(request):
    
    top_sellers = recent_trendy()
    context   = {
                    'top_sellers' : top_sellers
                }
    return render(request, 'home.html', context = context)