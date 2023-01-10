from django.shortcuts import render
from UserProfile.utils import utils
from datetime import datetime
# Create your views here.s

def home(request):

    return render(request, 'home.html', context = {})