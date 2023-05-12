from django.urls import path
from . import views

app_name = 'gamedb'
urlpatterns = [
    path('', views.gamedb, name='saledb'),
    path('ajax_db', views.ajax_db, name='ajax_db')
]