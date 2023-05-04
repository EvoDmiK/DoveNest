from datetime import datetime

from fastapi import FastAPI
from typing import Optional

from misc import template, utils


N_CONTENTS = 5

app = FastAPI()

@app.post("/")
def hello_world(): return {'Hello' : 'World!'}


@app.post("/items/{item_id}")
def read_item(item_id : int, query: Optional[str] = None): 
    return {"item_id" : item_id, "query" : query}


@app.post("/sales")
def sale_items(n_contents: int = 10, query: Optional[str] = None):

    return utils.get_sale_items(n_contents, query)



@app.post("/sales_kakao")
def sale_items_kakao(n_contents: int = 10, query: Optional[str] = None):

    datas = utils.get_sale_items(n_contents, query)
    return template.sale_template(datas)

    
@app.post("/greeting")
def greeting_kakao():

    return template.base_template()