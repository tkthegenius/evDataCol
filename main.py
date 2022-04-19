# In[]:
import requests 
import datetime
import pandas as pd 
from bs4 import BeautifulSoup


# In[]:
def organize(arr):
    returnArr = []
    for i in range(0,len(arr),2):
        appender = pd.concat([arr[i],arr[i+1]],ignore_index=True)
        returnArr.append(appender)
    return returnArr

# In[]:
def getURLs(URL):
    page = requests.get(URL)
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
        if checker == "United Kingdom":
            arrs_temp.append('pricing')
            print('added pricing')
        elif checker == "City - Cold Weather":
            if 'range' not in arrs_temp:
                arrs_temp.append('range')
                print('added range')
            else:
                arrs_temp.append('real energy consumption')
                print('added real energy consumption')
        elif checker == "Acceleration 0 - 100 km/h":
            arrs_temp.append('performance')
            print('added performance')
        elif checker == "Battery Capacity *":
            arrs_temp.append('battery')
            print('added battery')
        elif checker == "Charge Port":
            arrs_temp.append('charging')
            print('added charging')
        elif checker == "Range":
            if 'energy consumption' not in arrs_temp:
                arrs_temp.append('energy consumption')
                print('added energy consumption')
            else:
                arrs_temp.append('additional energy consumption')
                print('added additional energy consumption')
        elif checker == "Safety Rating":
            arrs_temp.append('safety')
            print('added safety')
        elif checker == "Length":
            arrs_temp.append('dimensions and weight')
            print('added dimensions and weight')
        elif checker == "Seats":
            arrs_temp.append('miscellaneous')
            print('added miscellaneous')
        elif checker == "Wall Plug (2.3 kW)":
            arrs_temp.append('charge specifications')
            print('added charge specifications')
        else:
            arrs_temp.append('additional information')
            print('added additional information')

    if len(arrs_temp) > len(tableTemp):
        for i in range(len(arrs_temp) - len(tableTemp)):
            arrs_temp.append("more information")
    arr = [arrs_temp,tableTemp]
    tuples = list(zip(*arr))
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
    return titleText, tuples, outputCell  

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
        out = pd.concat([out, tupleAdd(outputCell,key)])
    chargeSpecs = [tuples[len(tuples)-2],tuples[len(tuples)-1]]
    out = pd.concat([out,organizeCharge(chargeSpecs)])
    out.index.name = 'category'
    out.rename(columns = {0:title}, inplace=True)
    return out