#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests 
import pandas as pd 
from bs4 import BeautifulSoup
allInfo = {}
infoTest = {}
tempDict = pd.DataFrame({})
outputDict = pd.DataFrame({},columns = ['pricing', 'range', 'performance','charging','efficiency','real-consumption'])


# In[2]:


def createPriceCell(cell):
    outCell = pd.DataFrame(cell[0])
    appendCell = pd.DataFrame(cell[1][1])
    appendCell.rename(columns = {1:'Availability'}, inplace=True)
    prices = pd.concat([outCell, appendCell], axis =1)
    prices = prices.set_index([0])
    prices.rename(columns = {0:'Country',1:'Price'}, inplace=True)
    prices.index.name = 'Country'
    prices['Price'] = prices['Price'].map(lambda x: x.lstrip('Â£â‚¬'))
    return prices


# In[3]:


def straighten(arr):
    keys = []
    newDict = {}
    for tuple in arr:
        key = tuple[0]
        value = tuple[1]
        if key != 'charge specification':
            if key not in keys:
                keys.append(key)
            for i in range(len(value)-1,0,1):
                tempTuple = (value[0][i],value[1][i])
                print(tempTuple)
    return newDict


# In[4]:


page = requests.get('https://ev-database.uk/car/1541/MG-ZS-EV-Long-Range')


# In[ ]:


print(type(page))


# In[ ]:


soupTemp = BeautifulSoup(page.text, 'html.parser')


# In[ ]:


titleText = soupTemp.title.text


# In[ ]:


tableTemp = pd.read_html('https://ev-database.uk/car/1541/MG-ZS-EV-Long-Range')


# In[ ]:


for i in range(len(tableTemp)-1,0,-1):
    if tableTemp[i].empty:
        del tableTemp[i]


# In[ ]:


tuple1 = (tableTemp[0][0][0],tableTemp[0][1][0])
tuple1


# In[ ]:


arrs = ['pricing','pricing','range','range','performance','performance','charging','charging','efficiency','efficiency','efficiency','efficiency','real consumption','real consumption','dimensions','load data','miscellaneous','miscellaneous','BIK','BIK','BIK','BIK','BIK','BIK','charge specification','charge specification']


# In[ ]:


arr = [arrs,tableTemp]
tuples = list(zip(*arr))
tuples


# In[ ]:


keys = []
outputCell = {}
for tuple in tuples:
    key = tuple[0]
    value = tuple[1]
    if key != 'charge specification':
        if key not in keys:
            keys.append(key)
            for i in range(len(value)):
                tempTuple = (value[0][i],value[1][i])
                if i == 0:
                    outputCell[key] = tempTuple
                else:
                    outputCell[key] = outputCell[key],tempTuple
        else:
            for i in range(len(value)):
                tempTuple = (value[0][i],value[1][i])
                outputCell[key] = outputCell[key],tempTuple


# In[ ]:


out = pd.DataFrame(outputCell)


# In[ ]:


out.to_excel("test1622.xlsx")


# In[ ]:


for table in tableTemp:
    temp = pd.DataFrame(table)
    tempDict = pd.concat([tempDict,temp],axis=1)


# In[ ]:


tempDict.to_excel("test.xlsx")


# In[ ]:


with open(r'C:/Users/kimtae4/Desktop/Working/evDataCol/testIndex.html', "r") as f:
    page = f.read()
soup = BeautifulSoup(page, 'html.parser')


# In[ ]:


for smallID in ['pricing', 'range', 'performance','charging','efficiency','real-consumption']: 
    infoTest[smallID] = pd.read_html(str(soup.find('div',{'class':'data-table','id':smallID})))
    
infoTest


# In[ ]:


headers = soup.findAll('h2')
for head in headers:
    print(head)


# In[ ]:


rangeCell = soup.find('div',{'class':'data-table','id':'range'})
pd.read_html(rangeCell.text)


# In[ ]:


rawTable = pd.read_html('C:/Users/kimtae4/Desktop/Working/evDataCol/testIndex.html')
headers = 


# In[ ]:


for table in rawTable:
    print(table)
    print('|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||')


# In[ ]:


rawTable[0].info()


# In[ ]:





# In[ ]:





# In[ ]:




