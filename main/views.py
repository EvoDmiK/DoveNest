from django.shortcuts import render
from datetime import datetime
# Create your views here.s

def index(request):
    return render(request, 'home.html', context = {})