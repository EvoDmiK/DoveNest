from fastapi import FastAPI
from typing import Optional

app = FastAPI()

@app.post("/")
def hello_world(): return {'Hello' : 'World!'}

@app.post("/items/{item_id}")
def read_item(item_id : int, query: Optional[str] = None): 
    return {"item_id" : item_id, "query" : query}