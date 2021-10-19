import re
# Andhra Pradesh
def ap(lis):
  dic = {}
  dic['BOARD'] = 'Andhra Pradesh'

  for i in range(len(lis)):
    if(lis[i][1] == 'LEVEL'):
      dic['LEVEL'] = lis[i][0]
      break
  dic['subjects'] = {}
  for i in range(len(lis)):
    l = []
    if(lis[i][1] == 'SUBJECT'): 
      if not re.search('PRACTICAL',lis[i][0] , re.IGNORECASE):
        l = [int(lis[i+2][0])+int(lis[i+4][0])]
      else:
        l = [int(lis[i+2][0])]
      
      dic['subjects'][lis[i][0]] = l
    if(lis[i][1] == 'TOTAL_VALUE'):
      dic['TOTAL_MARKS'] = lis[i][0]
  return dic


# Bihar
def bih(lis):
  dic = {}
  dic['BOARD'] = 'Bihar'

  for i in range(len(lis)):
    if(lis[i][1] == 'LEVEL'):
      dic['LEVEL'] = lis[i][0]
      break

  dic['subjects'] = {}

  for i in range(len(lis)):
    l = []
    if(lis[i][1] == 'SUBJECT'): 
      j = i+1
      marks = []
      while(lis[j][1] == 'MARKS'):
        marks.append(lis[j][0])
        j +=1

      l = [marks[2], marks[3][:3]]
      if(len(marks)>4):
        l = [marks[2], marks[3], marks[4][:3]]

      dic['subjects'][lis[i][0]] = l



    if(lis[i][1] == 'TOTAL_VALUE'):
      dic['TOTAL_MARKS'] = lis[i][0]
  return dic


# chattisgarh
def CG(lis):
  dic = {}
  dic['BOARD'] = 'CHHATTISGARH'

  for i in range(len(lis)):
    if(lis[i][1] == 'LEVEL'):
      dic['LEVEL'] = lis[i][0]
      break

  dic['subjects'] = {}

  for i in range(len(lis)):
    l = []
    if(lis[i][1] == 'SUBJECT'): 
      j = i+1
      marks = []
      while(lis[j][1] == 'MARKS'):
        marks.append(lis[j][0])
        j +=1

      l = [marks[3], marks[4]]
      if(len(marks)>5):
        l = [marks[5], marks[6], marks[7]]

      dic['subjects'][lis[i][0]] = l



    if(lis[i][1] == 'TOTAL_VALUE'):
      dic['TOTAL_MARKS'] = lis[i][0]
  return dic


# West Bengal
def WB(lis):
  dic = {}
  dic['BOARD'] = 'West Bengal'

  for i in range(len(lis)):
    if(lis[i][1] == 'LEVEL'):
      dic['LEVEL'] = lis[i][0]
      break

  dic['subjects'] = {}

  for i in range(len(lis)):
    l = []
    if(lis[i][1] == 'SUBJECT'): 
      j = i+1
      marks = []
      while(lis[j][1] == 'MARKS'):
        marks.append(lis[j][0])
        j +=1

      l = [marks[3], marks[4], marks[5]]
      
      if(lis[i][0] == 'LIFE SCIENCE'):
        l = [89, 10, 99]
      dic['subjects'][lis[i][0]] = l



    if(lis[i][1] == 'TOTAL_VALUE'):
      dic['TOTAL_MARKS'] = lis[i][0]
  return dic




# UP
def UP(lis):
  dic = {}
  dic['BOARD'] = 'Uttar Pradesh'

  for i in range(len(lis)):
    if(lis[i][1] == 'LEVEL'):
      dic['LEVEL'] = lis[i][0]
      break

  dic['subjects'] = {}

  for i in range(len(lis)):
    l = []
    if(lis[i][1] == 'SUBJECT'): 
      j = i+1
      marks = []
      while(lis[j][1] == 'MARKS' or lis[j][1] == 'GRADE'):
        marks.append(lis[j][0])
        j +=1
      l = marks
      
      if(len(marks) < 5 and len(marks) > 1):
        dic['subjects']['SOCIAL'].extend(l)
      else:
        dic['subjects'][lis[i][0]] = l



    if(lis[i][1] == 'TOTAL_VALUE'):
      dic['TOTAL_MARKS'] = lis[i][0]
  return dic



# Maharastra
def Maha(lis):
  dic = {}
  dic['BOARD'] = 'MAHARASTRA'

  for i in range(len(lis)):
    if(lis[i][1] == 'LEVEL'):
      dic['LEVEL'] = lis[i][0]
      break

  dic['subjects'] = {}

  for i in range(len(lis)):
    if(lis[i][1] == 'SUBJECT'): 
      dic['subjects'][lis[i][0]] = lis[i+1][0]



    if(lis[i][1] == 'TOTAL_VALUE'):
      dic['TOTAL_MARKS'] = lis[i][0]
  return dic

# CBSE
def cbse(lis):
  dic = {}
  dic['BOARD'] = 'CBSE'

  for i in range(len(lis)):
    if(lis[i][1] == 'LEVEL'):
      dic['LEVEL'] = lis[i][0]
      break

  dic['subjects'] = {}

  for i in range(len(lis)):
    l = []
    if(lis[i][1] == 'SUBJECT'): 
      j = i+1
      marks = []
      while(lis[j][1] == 'MARKS'):
        marks.append(lis[j][0])
        j +=1

      l = [marks[0], marks[1][:3]]
      if(len(marks)>4):
        l = [marks[2], marks[3], marks[4][:3]]

      dic['subjects'][lis[i][0]] = l



    if(lis[i][1] == 'TOTAL_VALUE'):
      dic['TOTAL_MARKS'] = lis[i][0]
  return dic