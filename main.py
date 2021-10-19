from collections import Counter
import os
import glob
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import json
import re
from spell_checker import correction
from states import CG,UP,bih,Maha,ap,WB,cbse
from ner import test_model
from pathlib import Path
import re
import jsonify

from fastapi import FastAPI, File, UploadFile
app = FastAPI()

from typing import List
import shutil


model = ocr_predictor(pretrained=True)

def step1(img_path):
    doc = DocumentFile.from_images(img_path)
    result = model(doc)
    # result.show(doc)
    return result

def step2(result):
    json_output = result.export()
    num_words = len(json_output['pages'][0]['blocks'][0]['lines'][0]['words'])
    # checkConfidence = False
    words_list = []
    words_dic = json_output['pages'][0]['blocks'][0]['lines'][0]['words']


    for word in range(num_words):
        res = words_dic[word]['value']
        if not res.isdigit() and (words_dic[word]['confidence'] < 0.2):
            correct_word = correction(res.lower())
            # res = correct_word
            if(correct_word == 'lest'):
                res = 'West'
            if correct_word == res.lower() and len(correct_word)>1:
                res = ''
        words_list.append(res)

    total_text = ' '.join(words_list)

    punc = [')', '-', ':', '(', '$', '&']
    for p in punc:
        total_text = total_text.replace(p,"")

    return total_text


def classification(entitiess):
    classify = {'MUMBAI': 'maharastra',
       'State': 'maharastra',
       'State of Secondary and Board Higher Pune': 'maharastra',
       'Hyderabad': 'Andhra Pradesh',
       'Uttar': 'UP',
       'Uttar Pradesh':'UP',
       'Pradesh Uttar': 'UP',
       'COUNCIL FOR THE INDIAN SCHOOL': 'ICSE',
       'CENTRAL': 'CBSE',
       'CENTRAL SECONDARY BOARD': 'CBSE',
       'KERALA' : 'KERALA',
       'KARNATAKA' : 'KARNATAKA',
       'Bengal': 'West Bengal',
       'West': 'West Bengal',
       'BIHAR': 'BIHAR',
       'PATNA': 'BIHAR',
       'CHHATTISGARH': 'CHHATTISGARH',
       }
    
    board_name = ''
    for en in entitiess:
        if (en[1] == 'BOARD'):
            board_name = classify[en[0]]
            return board_name


def json_output(board_name,entitiess,img_path):
    funCall = {
    'maharastra': Maha,
    'Andhra Pradesh': ap,
    'UP': UP,
    'BIHAR': bih,
    'CHHATTISGARH': CG,
    'West Bengal': WB,
    'CBSE': cbse
    }

    json_data = funCall[board_name](entitiess)

    json_string = json.dumps(json_data, indent=2)
    img_path = img_path[:-4] + '.json'
    file_location = f"details/{img_path}"
    with open(file_location, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    return json_string



js_data = {}

@app.post("/upload")
async def upload(uploaded_file: List[UploadFile] = File(...)): 
    global js_data

    for img in uploaded_file:
        file_location = f"uploaded/{img.filename}"
        with open(file_location, "wb") as file_object:
            shutil.copyfileobj(img.file, file_object)  

        id_name = img.filename[:-4]
        js_data[id_name] = "Not Processed"
    
    json_str = json.dumps(js_data)


    # print(js_data)

    return json_str

@app.get("/fileinfo")
async def fileinfo(fileid):
    global js_data
    print(js_data)
    j_str = js_data[fileid]

    return j_str

    # no param
    # return name ,status of the files
    # return an array with this details above 

@app.get("/filedetails")
async def fileDetails(fileid):
    json_res = ''
    path = 'C:\\Users\\Nikhil\\Desktop\\final_demo\\details'
    filename = str(fileid) + '.json'
    for filename in glob.glob(os.path.join(path, filename)):
        with open(os.path.join(os.getcwd(), filename), 'r') as data_file: 
            data = json.load(data_file)
            json_res = data
    
    global js_data
    js_data[fileid] = "Processing"

    return json_res

@app.post("/processed")
async def process_image(fileid):
    global js_data
    js_data[fileid] = "Processed"
    return 'final_demo\\' + str(fileid) + '.png'
    


@app.post("/")
async def root():
    
    lst = []    
    file = 'C:\\Users\\Nikhil\\Desktop\\final_demo\\uploaded'
    for filename in os.listdir(file):
        if filename.endswith(".png"):
            res = step1(filename)
            total_text = step2(res)
            ent = test_model(total_text)
            board_name = classification(ent)
            json_string = json_output(board_name,ent,filename)
            lst.append(json_string)
            fileid = filename[:-4]

            global js_data
            js_data[fileid] = "Processing"


    return lst

