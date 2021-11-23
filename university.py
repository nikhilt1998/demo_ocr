from __future__ import unicode_literals, print_function
from pathlib import Path
import spacy
import json



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

def getText(bboxes, orientation):

  crrt_bboxes = []

  op = {}
  op["CGPA"] = ''
  op["SGPA"] = ''
  op["Orientation"] = ''


  if(orientation == 'H'):
        
    crrt_bboxes = getLine(bboxes)

    for i in range(len(crrt_bboxes)):
      for j in range(len(crrt_bboxes[i])):
        if( "CGPA" in crrt_bboxes[i][j][4].upper() or "SGPA" in crrt_bboxes[i][j][4].upper() ):
          for k in range(j+1,len(crrt_bboxes[i])):
            try:
              if( "CGPA" in crrt_bboxes[i][k][4].upper() or "SGPA" in crrt_bboxes[i][k][4].upper()):
                return
              
              num = float(crrt_bboxes[i][k][4].replace(":",""))
              
              if(0<num<=10):
                op["Orientation"] = "horizontal"
                if(len(op[crrt_bboxes[i][j][4].upper().replace(":","")])==0):
                  op[crrt_bboxes[i][j][4].upper().replace(":","")] = str(num)
                break
              else:
                raise Exception()
            except:
              temp=0

  if(orientation == 'V'):

    for word in bboxes:
      if( "CGPA" in word[4].upper() or "SGPA" in word[4].upper() ):
        for number in bboxes:
          
          if(word[0] < (number[0]+number[2])//2 < word[2] and number[1] > word[1]):
            
            if( "CGPA" in number[4].upper() or "SGPA" in number[4].upper() ):
              break
            try:
              num = float(number[4].replace(":",""))
              if(0<num<=10):
                op["Orientation"] = "Vertical"
                if(len(op[word[4].upper().replace(":","")])==0):
                  op[word[4].upper().replace(":","")] = str(num)
                break
              else:
                raise Exception()
            except:
              temp=0
  return op

#_______________________________________________________________________________

def ner_model(text, nlp_test) :
  doc = nlp_test(text)
  entities = [(ent.text, ent.label_) for ent in doc.ents]
  docx = {}
  docx['University'] = []
  docx['Subjects'] = []
  docx['Grade'] = []
  for i in range(len(entities)):
    if (entities[i][1] == 'UNIVER'):
      docx['University'].append(entities[i][0])
    if (entities[i][1] == 'SUBJECT'):
      docx['Subjects'].append(entities[i][0])
    if (entities[i][1] == 'GRADE'):
      docx['Grade'].append(entities[i][0])
  docx['University'] = ' '.join(docx['University'])

  return docx
#_______________________________________________________________________________

def getGPA_new(result):

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

  output_dir=Path("ner/ner_university_gpa")


  nlp_test = spacy.load(output_dir)

  crrt_bboxes = getLine(bboxes)
  text = ' '.join([desired[-1] for cord in crrt_bboxes for desired in cord])
  grades = ner_model(text, nlp_test)


  op = getText(bboxes, 'H')
  if op is None:
    op = getText(bboxes, 'V')
  
  for key, value in op.items():
    if(key != 'Orientation'):
      grades[key] = value

  # return json.dumps(grades)
  return grades
