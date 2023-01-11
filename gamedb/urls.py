from django.urls import path
from . import views

app_name = 'gamedb'
urlpatterns = [
    path('', views.gamedb, name='saledb'),
]