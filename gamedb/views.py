from django.shortcuts import render
from UTILS import utils

DB = utils.salesDB(table_name = 'saleinfo', db_name = 'game_informations')
def gamedb(request):

    datas   = DB.search_table(how_many = 5)
    context = {'datas' : datas}
    return render(request, 'sales.html', context = context)



