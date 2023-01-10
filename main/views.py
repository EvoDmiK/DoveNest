from django.shortcuts import render
from datetime import datetime
from UTILS import utils
# Create your views here.s

def home(request):
    
    top_sellers = utils.top_sellers()
    context   = {
                    'top_sellers' : top_sellers
                }
    return render(request, 'home.html', context = context)