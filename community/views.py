from django.shortcuts import render
from datetime import datetime
# Create your views here.s

def community(request):
    return render(request, 'community.html', context = {})