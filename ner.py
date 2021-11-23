from __future__ import unicode_literals, print_function
import plac
import random
from pathlib import Path
import spacy
from spacy import displacy
from tqdm import tqdm 
import nltk

import os
import glob

import re
import json
import warnings
warnings.filterwarnings('ignore')

def createTrainingData(path):

  TRAIN_DATA = []

  for filename in glob.glob(os.path.join(path, '*.json')):
   with open(os.path.join(os.getcwd(), filename), 'r') as data_file: 
      data = json.load(data_file)
      # print(data[0])
      dic = {}
      lis = []
      for l in data[0]['entities']:
        tup = (l[0] , l[1], l[2])
        lis.append(tup)
      dic['entities'] = lis

      fil = (data[0]['content'], dic)

      TRAIN_DATA.append(fil)

  return TRAIN_DATA

model_dir =Path("ner/ner_states")

def trainNER(TRAIN_DATA,model=None, output_dir=model_dir, n_iter=150):
  if model is not None:
    nlp = spacy.load(model)  
    print("Loaded model '%s'" % model)
  else:
    nlp = spacy.blank('en')  
    print("Created blank 'en' model")

  # Setup the pipeline

  if 'ner' not in nlp.pipe_names:
      ner = nlp.create_pipe('ner')
      nlp.add_pipe(ner, last=True)
  else:
      ner = nlp.get_pipe('ner')
  
  # Train recognizer

  for _, annotations in TRAIN_DATA:
      for ent in annotations.get('entities'):
          ner.add_label(ent[2])

  other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
  with nlp.disable_pipes(*other_pipes):  # only train NER
      optimizer = nlp.begin_training()
      for itn in range(n_iter):
          random.shuffle(TRAIN_DATA)
          losses = {}
          for text, annotations in tqdm(TRAIN_DATA):
              nlp.update(
                  [text],  
                  [annotations],  
                  drop=0.5,  
                  sgd=optimizer,
                  losses=losses)
          print('iter:', itn, 'loss:', losses)

  # Save the model

  if output_dir is not None:
      output_dir = Path(output_dir)
      if not output_dir.exists():
          output_dir.mkdir()
      nlp.to_disk(output_dir)
      print("Saved model to", output_dir)

def test_model(total_text, output_dir = model_dir):
  nlp = spacy.load(output_dir)
  text = total_text
  doc = nlp(text)
  entitiess = [(ent.text, ent.label_) for ent in doc.ents]

  return entitiess

