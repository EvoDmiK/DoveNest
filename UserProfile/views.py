from django.shortcuts import render
from datetime import datetime
# Create your views here.s

def profile(request):
    return render(request, 'profile.html', context = {})