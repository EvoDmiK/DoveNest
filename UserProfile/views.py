from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime
from UTILS import utils
import json

KEY     = utils.get_key()
USER_ID = 76561198804867273

def profile(request):

    library     = utils.SteamAPI.get_user_library(KEY, USER_ID)
    most_played = utils.SteamAPI.most_played(library)

    genre_stat, developer_stat, num_games  = utils.SteamAPI.get_stats(library)
    context = {
            'datas'          : most_played,
            'num_games'      : num_games,
            'genre_stat'     : genre_stat,
            'developer_stat' : developer_stat,
        }
    return render(request, 'profile.html', context = context)


def ajax_profile(request):

    if request.method == "POST":
    
        tag_id = json.loads(request.body)['id']
        print(f'Ajax 민수야 고맙다 : {tag_id}')

        if tag_id.lower() == "steam":
            library     = utils.SteamAPI.get_user_library(KEY, USER_ID)
            most_played = utils.SteamAPI.most_played(library)

            genre_stat, developer_stat, num_games  = utils.SteamAPI.get_stats(library)
            context = {
                    'datas'           : most_played,
                    'num_games'       : num_games,
                }
            
        elif tag_id.lower() == "riot":
            context = {"num_games" : 2000}

        else: context = {"num_games" : 3000}
        return JsonResponse(context)


