from django.shortcuts import render
from datetime import datetime
# Create your views here.s

def news(request):
    return render(request, 'news.html', context = {})