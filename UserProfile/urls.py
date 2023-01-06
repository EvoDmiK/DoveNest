from django.urls import path
from . import views

app_name = 'profile'
urlpatterns = [
    path('', views.profile, name='profile'),
    path('ajax_profile', views.ajax_profile, name='ajax_profile')
]