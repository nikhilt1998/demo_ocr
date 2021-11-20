import os
import glob
from doctr.io import DocumentFile
from doctr.utils.visualization import visualize_page
from doctr.models import ocr_predictor
import json
import re
from spell_checker import correction
from states import CG,UP,bih,Maha,ap,WB,cbse,ICSE
from ner import test_model
from university import getGPA_new
from univer_spl import get_Grand_total
from deg_cert import get_dc_details
from pathlib import Path
import re
import jsonify
import msgpack
from redis import Redis

model = ocr_predictor(pretrained=True)
default_dict={"Status":"Processing","Details":{}}
redis = Redis(host="redis")

def set_dict_redis(key,dictionary):
    redis.set(key, msgpack.packb(dictionary))

def get_dict_redis(key):
    value = redis.get(key)
    return (msgpack.unpackb(value))

# def temp(something):
#     return something

def step1(img_path):
    print("----------------> Step 1")
    doc = DocumentFile.from_images(img_path)
    result = model(doc)
    fig = visualize_page(result.pages[0].export(), doc[0], interactive=False)
    l = img_path.split("/")[-1]
    print(l)
    file_location = "processed/"+l
    fig.savefig(file_location)
    return result

def step2(result):
    print("----------------> Step 2")
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



def stateClassification(entitiess):
    classify = {'MUMBAI': 'maharastra',
       'State': 'maharastra',
       'State of Secondary and Board Higher Pune': 'maharastra',
       'Hyderabad': 'Andhra Pradesh',
       'Uttar': 'UP',
       'Uttar Pradesh':'UP',
       'Pradesh Uttar': 'UP',
       'COUNCIL': 'ICSE',
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


def json_output_board(board_name,entitiess,img_path):
    funCall = {
    'maharastra': Maha,
    'Andhra Pradesh': ap,
    'UP': UP,
    'BIHAR': bih,
    'CHHATTISGARH': CG,
    'West Bengal': WB,
    'CBSE': cbse,
    'ICSE': ICSE
    }

    json_data = funCall[board_name](entitiess)
    return json_data



def isUniversityCertificate(result):
    export = result.export()
    num_words = len(export['pages'][0]['blocks'][0]['lines'][0]['words'])
    # checkConfidence = False
    words_list = []
    words_dic = export['pages'][0]['blocks'][0]['lines'][0]['words']
    
    for word in range(num_words):
        res = words_dic[word]['value']
        words_list.append(res)

    keywords_university_marksheets = ['university', 'engineering', 'Engineering','(UNIVERSITY', 'management', 'SGPA', 'UNIVERSITY', 'UNIVERSITY,BELAGAVI']

    print(words_list)

    if ("certifies" in (key.lower() for key in words_list) \
    or "certificate" in (key.lower() for key in words_list) \
    or 'probisional' in (key.lower() for key in words_list)):
      return "dc"

    flag = 0
    sgpa_keys = ['SGPA:','SGPA','sgpa']
    for key in keywords_university_marksheets:
        if key in words_list:
            for k in sgpa_keys:
              if k in words_list:
                flag = 1
                return "uni_grades"
            if flag == 0:
              return "uni_marks"

    return "board"
    

def pipeline(filename):
    print("----------------> Pipeline")
    key=filename.split(".")[0]
    set_dict_redis(key,default_dict)  
    file = r'uploaded'
    res = step1("uploaded/"+filename)
    
    category = isUniversityCertificate(res)

    if(category == "dc"):
        print("dc")
        json_data = get_dc_details(res)
    elif(category == "uni_grades"):
        print("uni_grades")
        json_data = getGPA_new(res)
    elif(category == "uni_marks"):
        print("uni_marks")
        json_data = get_Grand_total(res)
    else:
        total_text = step2(res)
        ent = test_model(total_text)
        board_name = stateClassification(ent)
        json_data = json_output_board(board_name,ent,filename)

    new_dict={}
    new_dict["Details"]=json_data
    new_dict["Status"]="Processed"
    set_dict_redis(key,new_dict)
    return filename

