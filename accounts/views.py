from django.shortcuts import render
from datetime import datetime
# Create your views here.s

def signin(request):
    return render(request, 'login.html', context = {})