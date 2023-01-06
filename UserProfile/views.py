from django.shortcuts import render
from datetime import datetime
from .utils import utils

KEY     = utils.get_key()
USER_ID = 76561198032052956

def profile(request):

    library     = utils.get_user_library(KEY, USER_ID)
    most_played = utils.most_played(library)

    genre_stat, developer_stat, num_games  = utils.get_stats(library)
    context = {
            'datas'      : most_played,
            'num_games'  : num_games,
            'genre_stat' : genre_stat,
        }
    return render(request, 'profile.html', context = context)