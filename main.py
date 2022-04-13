# In[]:
import requests 
import datetime
import pandas as pd 
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

URL = 'https://ev-database.org/car/1252/BMW-i4-eDrive40'

# In[]:
def organize(arr):
    returnArr = []
    for i in range(0,len(arr),2):
        appender = pd.concat([arr[i],arr[i+1]],ignore_index=True)
        returnArr.append(appender)
    return returnArr

# In[]:
def getURLs(URL):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    page = session.get(URL)
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
        checker = smallArr[0][0]
        if checker == "United Kingdom":
            arrs_temp.append('pricing')
        elif checker == "City - Cold Weather":
            if 'range' not in arrs_temp:
                arrs_temp.append('range')
            else:
                arrs_temp.append('real energy consumption')
        elif checker == "Acceleration 0 - 100 km/h":
            arrs_temp.append('performance')
        elif checker == "Battery Capacity":
            arrs_temp.append('battery')
        elif checker == "Charge Port":
            arrs_temp.append('charging')
        elif checker == "Range":
            if 'energy consumption' not in arrs_temp:
                arrs_temp.append('energy consumption')
            else:
                arrs_temp.append('additional energy consumption')
        elif checker == "Safety Rating":
            arrs_temp.append('safety')
        elif checker == "Length":
            arrs_temp.append('dimensions and weight')
        elif checker == "Seats":
            arrs_temp.append('miscellaneous')
        elif checker == "Wall Plug (2.3 kW)":
            arrs_temp.append('charge specifications')
        else:
            arrs_temp.append('additional information')

        """ 
        match smallArr[0][0]:
            case "United Kingdom":
                arrs_temp.append('pricing')
            case "City - Cold Weather":
                if 'range' not in arrs_temp:
                    arrs_temp.append('range')
                else:
                    arrs_temp.append('real energy consumption')
            case "Acceleration 0 - 100 km/h":
                arrs_temp.append('performance')
            case "Battery Capacity":
                arrs_temp.append('battery')
            case "Charge Port":
                arrs_temp.append('charging')
            case "Range":
                if 'energy consumption' not in arrs_temp:
                    arrs_temp.append('energy consumption')
                else:
                    arrs_temp.append('additional energy consumption')
            case "Safety Rating":
                arrs_temp.append('safety')
            case "Length":
                arrs_temp.append('dimensions and weight')
            case "Seats":
                arrs_temp.append('miscellaneous')
            case "Wall Plug (2.3 kW)":
                arrs_temp.append('charge specifications')
        """

    """ arrs = ['pricing','pricing','range','range','performance','performance','charging','charging','efficiency','efficiency','efficiency','efficiency','real consumption','real consumption','dimensions','load data','miscellaneous','miscellaneous','BIK','BIK','BIK','BIK','BIK','BIK','charge specification','charge specification'] """

    if len(arrs_temp) > len(tableTemp):
        for i in range(len(arrs_temp) - len(tableTemp)):
            arrs_temp.append("additional information")
    arr = [arrs_temp,tableTemp]
    tuples = list(zip(*arr))
    # In[]:
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

# In[ ]:
out = createDataBase(URL)
now = datetime.datetime.now()
dateNTime = now.strftime("%Y%m%d_%H%M%S_")
out.to_excel(dateNTime + "EV_Data_Database.xlsx")
