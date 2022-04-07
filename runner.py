#!/usr/bin/env python
# coding: utf-8

# In[1]:
import requests 
import pandas as pd 
from bs4 import BeautifulSoup
outputDict = pd.DataFrame({},columns = ['pricing', 'range', 'performance','charging','efficiency','real-consumption'])

# In[]:
def organizeCharge(tupleArr):
    output = pd.DataFrame({})
    for i in range(len(tupleArr)):
        details = tupleArr[i][1]
        keys = details.keys()
        details2 = details.drop(keys[0], axis=1)
        details['join'] = details2.apply('----'.join, axis=1)
        tempOutput = details[[keys[0],'join']].apply(tuple, axis=1)
        output = pd.concat([output, tempOutput])
    idx = pd.Series(['charge specification']*len(output))
    output = output.set_index(idx)
    output.rename(columns={0:titleText},inplace=True)
    return output

# In[4]:
page = requests.get('https://ev-database.uk/car/1541/MG-ZS-EV-Long-Range')
soupTemp = BeautifulSoup(page.text, 'html.parser')
titleText = soupTemp.title.text
tableTemp = pd.read_html('https://ev-database.uk/car/1541/MG-ZS-EV-Long-Range')


# In[ ]:
for i in range(len(tableTemp)-1,0,-1):
    if tableTemp[i].empty:
        del tableTemp[i]

# In[ ]:
arrs = ['pricing','pricing','range','range','performance','performance','charging','charging','efficiency','efficiency','efficiency','efficiency','real consumption','real consumption','dimensions','load data','miscellaneous','miscellaneous','BIK','BIK','BIK','BIK','BIK','BIK','charge specification','charge specification']
arr = [arrs,tableTemp]
tuples = list(zip(*arr))

# In[ ]:
keys = []
outputCell = {}
for x in tuples:
    key = x[0]
    value = x[1]
    if key != 'charge specification':
        if key not in keys:
            outputCell[key] = []
            keys.append(key)
            for i in range(len(value)):
                tempTuple = (value[0][i],value[1][i])
                outputCell[key].append(tempTuple)
        else:
            for i in range(len(value)):
                tempTuple = (value[0][i],value[1][i])
                outputCell[key].append(tempTuple)


# In[ ]:
def tupleAdd(adder, title):
    addDf = pd.Series(adder[title]).to_frame(titleText)
    idx = pd.Series([title]*len(adder[title]))
    addDf = addDf.set_index(idx)
    return addDf     

# In[ ]:
out = pd.DataFrame({})
for key in outputCell.keys():
    out = pd.concat([out, tupleAdd(outputCell,key)])
out.index_name = "category"


# In[ ]:

tester = [tuples[len(tuples)-2],tuples[len(tuples)-1]]
out = pd.concat([out,organizeCharge(tester)])
out.to_excel("test_1519070422.xlsx")
