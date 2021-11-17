import re
import json
import spacy
from pathlib import Path


#bangalore univ
def beng(text, entities):
  regex = "(\d{2,3} +)(\d{1,3} +)(\d{1,3} +)?"
  match = re.findall(regex, text)
  subjects = []
  docx = {}
  docx['UNIVERSITY'] = []
  for ent in entities:
    if(ent[1] == 'SUBJECT'):
      subjects.append(ent[0])
    elif(ent[1] == 'TOTAL'):
      docx['GRAND TOTAL'] = ent[0]
    elif(ent[1] == 'RESULT'):
      docx['RESULT'] = ent[0]
    elif ent[1] == 'UNIVER':
      docx['UNIVERSITY'].append(ent[0])
  docx['UNIVERSITY'] = ' '.join(docx['UNIVERSITY'])
  for i in range(len(subjects)):
    docx[subjects[i]] = (match[3*(i+1)-2][-1], match[3*(i+1)-1][-2])
  docx = json.dumps(docx, indent=2)    
  return docx


#visvesaraya univ
def vtu(text, entities):
  regex = "(\d{2,3} +)(\d{2,3} +)(\d{2,3} +)(\d{2,3} +)(\d{2,3} +)(\d{2,3} +)(\d{2,3} +)(\d{2,3} +)(\d{2,3} +)?"
  match = re.findall(regex, text)
  subjects = []
  docx = {}
  docx['UNIVERSITY'] = []
  for ent in entities:
    if(ent[1] == 'SUBJECT'):
      subjects.append(ent[0])
    elif(ent[1] == 'TOTAL'):
      docx['GRAND TOTAL'] = ent[0]
    elif(ent[1] == 'RESULT'):
      docx['RESULT'] = ent[0]
    elif ent[1] == 'UNIVER':
      docx['UNIVERSITY'].append(ent[0])
  docx['UNIVERSITY'] = ' '.join(docx['UNIVERSITY'])
  if(len(subjects) == len(match)):
    for i in range(len(match)):
      if list(match[i])[-1] == '':
        docx[subjects[i]] = (match[i][2], match[i][4], match[i][7])
      else:
        docx[subjects[i]] = (match[i][2], match[i][5], match[i][8])
  docx = json.dumps(docx, indent=2)    
  return docx



def getLine(bboxes):
  crrt_bboxes = []

  new_bboxes = sorted(bboxes, key = lambda x: ( (x[1]+x[3])//2, (x[0]+x[2])//2))
  ini = new_bboxes[0]
  threshold_value_y = (ini[3] - ini[1])//2

  crrt_bboxes.append([ini])

  for i in range(1, len(new_bboxes)):
    if( abs((new_bboxes[i][1] + new_bboxes[i][3]) - (ini[1] + ini[3]))//2 < threshold_value_y) :
      crrt_bboxes[-1].append(new_bboxes[i])
      ini = new_bboxes[i]
    else:
      crrt_bboxes[-1] = sorted(crrt_bboxes[-1], key = lambda x: x[0])
      ini = new_bboxes[i]
      crrt_bboxes.append([ini])  
    threshold_value_y = (ini[3] - ini[1])//2
  crrt_bboxes[-1] = sorted(crrt_bboxes[-1], key = lambda x: x[0])
  return crrt_bboxes


def get_Grand_total(result):

  export = result.export()

  # Flatten the export
  page_words = [[word for block in page['blocks'] for line in block['lines'] for word in line['words']] for page in export['pages']]
  page_dims = [page['dimensions'] for page in export['pages']]

  # Get the coords in [xmin, ymin, xmax, ymax]
  words_abs_coords = [
      [[int(round(word['geometry'][0][0] * dims[1])), int(round(word['geometry'][0][1] * dims[0])), int(round(word['geometry'][1][0] * dims[1])), int(round(word['geometry'][1][1] * dims[0])), word['value']] for word in words]
      for words, dims in zip(page_words, page_dims)
  ]
  bboxes = words_abs_coords[0]

  output_dir=Path("ner/ner_spl")


  nlp_test = spacy.load(output_dir)

  crrt_bboxes = getLine(bboxes)
  text = ' '.join([desired[-1] for cord in crrt_bboxes for desired in cord])

  doc = nlp_test(text)
  entities = [(ent.text, ent.label_) for ent in doc.ents]

  for ent in entities:
    if ent[1] == 'UNIVER':
        if(ent[0] in 'BANGALORE UNIVERSITY'):
            beng(text, entities)
        else:
            vtu(text, entities)


