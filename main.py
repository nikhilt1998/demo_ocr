from importlib import reload
import uvicorn
from collections import Counter
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from job import set_dict_redis,get_dict_redis,pipeline
from rq import Queue
from redis import Redis
import glob
q = Queue(connection=Redis(host='redis'))
app = FastAPI()

from typing import List
import shutil
default_dict={"Status":"Unprocessed","Details":{}}



@app.post("/upload")
async def upload(uploaded_file: List[UploadFile] = File(...)): 
    for img in uploaded_file:
        file_location = f"uploaded/{img.filename}"
        with open(file_location, "wb") as file_object:
            shutil.copyfileobj(img.file, file_object)  
        key = img.filename.split('.')[0]
        set_dict_redis(key,default_dict)
        print(q)
        q.enqueue(pipeline,img.filename)
    return "done"

@app.get("/fileinfo")
async def fileinfo():
    list_files=glob.glob("uploaded/*.png")
    keys=[x.split("/")[-1].split('.')[0] for x in list_files]
    all={}
    for key in keys:
        temp=get_dict_redis(key)
        all[key]= temp["Status"]
    return all

@app.get("/filedetails")
async def fileDetails(fileid):
    temp=get_dict_redis(fileid)
    return temp

@app.post("/processed")
async def process_image(fileid):
    response = FileResponse(path='processed/'+fileid+".png",media_type="image/png")
    return response
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


