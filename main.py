# In[]:
import requests 
import datetime
import time
import pandas as pd 
from bs4 import BeautifulSoup

# In[]:
def organize(arr):
    returnArr = []
    for i in range(0,len(arr),2):
        cols = arr[i].columns
        if len(cols) == 1:
            pass
        if i == len(arr)-1:
            appender = pd.DataFrame(arr[i])
        else:
            appender = pd.concat([arr[i],arr[i+1]],ignore_index=True,sort=False)
        returnArr.append(appender)
    return returnArr

# In[]:
def getURLs(URL):
    print ("URL: ", URL)
    page = requests.get(URL)
    print(page.status_code)
    if page.status_code == 429:
        raise ConnectionError("Congratulations! You have been successfully blacklisted by this website. You can try again in 2 days, or on someone else's computer that hasn't been used yet.")
    soupTemp = BeautifulSoup(page.text, 'html.parser')
    titleText = soupTemp.title.text
    titleText = titleText.split('price')[0]
    tableTemp = pd.read_html(URL)

    for i in range(len(tableTemp)-1,0,-1):
        if tableTemp[i].empty:
            del tableTemp[i]
    
    tableTemp = organize(tableTemp)

    arrs_temp = []
    for smallArr in tableTemp:
        checker = smallArr.columns[0]
        if type(checker) == tuple:
            checker = checker[0]
        checker = smallArr[checker][0]
        if "United Kingdom" in checker:
            arrs_temp.append('pricing')
        elif "City - Cold Weather" in checker :
            if 'range' not in arrs_temp:
                arrs_temp.append('range')
            else:
                arrs_temp.append('real energy consumption')
        elif "Acceleration 0 - 100 km/h" in checker :
            arrs_temp.append('performance')
        elif "Battery Capacity" in checker:
            arrs_temp.append('battery')
        elif "Charge Port" in checker:
            arrs_temp.append('charging')
        elif "Range" in checker:
            if 'energy consumption' not in arrs_temp:
                arrs_temp.append('energy consumption')
            else:
                arrs_temp.append('additional energy consumption')
        elif "Safety Rating" in checker:
            arrs_temp.append('safety')
        elif "Length" in checker:
            arrs_temp.append('dimensions and weight')
        elif "Seats" in checker:
            arrs_temp.append('miscellaneous')
        elif "Wall Plug (2.3 kW)" in checker:
            arrs_temp.append('charge specifications')
        else:
            arrs_temp.append('additional information')

    if len(arrs_temp) < len(tableTemp):
        for i in range(len(tableTemp) - len(arrs_temp)):
            arrs_temp.append("more information")
    arr = [arrs_temp,tableTemp]
    tuples = list(zip(*arr))
    keys = []
    outputCell = {}
    for x in tuples:
        key = x[0]
        value = x[1]
        if key != 'charge specifications':
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
    return titleText, tuples, outputCell  

# In[]:
def organizeCharge(details):
    output = pd.DataFrame({})    
    details = details[1]
    keys = details.keys()
    details2 = details.drop(keys[0], axis=1)
    details['join'] = details2.apply(lambda row: '----'.join(row.values.astype(str)), axis=1)
    tempOutput = details[[keys[0],'join']].apply(tuple, axis=1)
    output = pd.concat([output, tempOutput],sort=False)
    idx = pd.Series(['charge specification']*len(output))
    output = output.set_index(idx)
    return output

# In[ ]:
def tupleAdd(adder, title):
    addDf = pd.Series(adder[title]).to_frame()
    idx = pd.Series([title]*len(adder[title]))
    addDf = addDf.set_index(idx)
    return addDf     

# In[ ]:
def createDataBase(URL):
    title, tuples, outputCell = getURLs(URL)
    out = pd.DataFrame({})
    for key in outputCell.keys():
        out = pd.concat([out, tupleAdd(outputCell,key)],sort=False)
    for item in tuples:
        if "Charging Point" in item[1].columns:
            chargeSpecs = item
    out = pd.concat([out,organizeCharge(chargeSpecs)],sort=False)
    out.index.name = 'category'
    print(title)
    out.rename(columns = {0:title}, inplace=True)
    return out
# %%
