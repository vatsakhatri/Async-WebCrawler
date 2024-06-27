import time
from fastapi import FastAPI
from tasks import crawl,ping_for_result
from celery.result import AsyncResult
from celer import capp as cel
app = FastAPI()

@app.post('/crawl')
def add_from_fast():
    task = crawl.delay()
    return {"task_id": task.id}

@app.get("/ping/{id}")
def get_status(id:str):
    
    ping_for_result.delay(id)
    return{"pinging started":"for status"} 

@app.post('/complete')
def com():
    print("thee summary is finished")
    return {"ok":"ok"}
    