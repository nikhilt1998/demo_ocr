import re
import json
import spacy
from pathlib import Path






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


def get_dc_details(result):

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

  output_dir=Path("ner/dc")


  nlp_test = spacy.load(output_dir)

  crrt_bboxes = getLine(bboxes)
  text = ' '.join([desired[-1] for cord in crrt_bboxes for desired in cord])

  doc = nlp_test(text)
  entities = [(ent.text, ent.label_) for ent in doc.ents]
  
  docx = {}
  docx['University'] = []
  docx['Subject'] = []
  docx['Result'] = []
  docx['USN'] = []
  for i in range(len(entities)):
    if (entities[i][1] == 'UNIVER'):
      docx['University'].append(entities[i][0])
    if (entities[i][1] == 'SUBJECT'):
      docx['Branch'].append(entities[i][0])
    if (entities[i][1] == 'RESULT'):
      docx['Result'].append(entities[i][0])
    if (entities[i][1] == 'USN'):
      docx['USN'].append(entities[i][0])
  
  docx = json.dumps(docx, indent=2)    
  return docx


