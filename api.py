from datetime import datetime

from fastapi import FastAPI
from typing import Optional

from misc import utils

DB         = utils.SalesDB(table_name = 'discounts', db_name = 'sale_informations')
N_CONTENTS = 5

app = FastAPI()


@app.post("/")
def hello_world(): return {'Hello' : 'World!'}

@app.post("/items/{item_id}")
def read_item(item_id : int, query: Optional[str] = None): 
    return {"item_id" : item_id, "query" : query}


@app.post("/sales")
def sale_items(query: Optional[str] = None, n_contents: int = 10):

    NOW     = datetime.now()
    Y, M, D = NOW.year, NOW.month, NOW.day

    datas   = {}
    today   = f'{Y}{str(M).zfill(2)}{str(D).zfill(2)}'

    sorting_ = query if query != None else 'idx'
    desc     = True  if sorting_ in ['percent', 'name'] else False
    db_datas = DB.search_table(
                                how_many = n_contents, conditions  = ['date', today],
                                desc     =       desc, sorting_col = sorting_
                            )

    for idx, db_data in enumerate(db_datas):

        _, appid, name, percent, original, discounted, platform, _ = db_data

        json_data = utils.SteamAPI.get_info(appid)
        genre     = utils.SteamAPI.get_genre(appid, platform)

        try:

            data = {
                        'image'       : json_data['header_image'],
                        'name'        : json_data['name'],
                        'genre'       : genre,
                        'original'    : f'₩ {original:,}',
                        'percentage'  : f'-{percent}%',
                        'discounted'  : f'₩ {discounted:,}',
                        'steam_page'  : f'{utils.SteamAPI.URLS["steam_page"]}/{appid}'
                    }

            datas[idx] = data

        except Exception as e:
                print(f'[WARN.D.A-0001] <{appid}> 현재 그 컨텐츠는 {platform}에서 제공 되지 않습니다. {e}')

        
    return {"data" : datas}
