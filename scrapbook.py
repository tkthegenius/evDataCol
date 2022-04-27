# In[]:
from __future__ import print_function
import os
import os.path
import sys
import json
import time
import datetime
import numpy as np
import pandas as pd
from gooey import Gooey, GooeyParser


def mustBeDir(pathway):
    if os.path.isdir(pathway):
        return pathway
    else:
        raise TypeError(
            "What you provided is not a directory. Please enter a valid directory")


def mustBeFile(pathway):
    if os.path.isfile(pathway):
        return pathway
    else:
        raise TypeError(
            "What you provided is not a directory. Please enter a valid file")


@Gooey(program_name="Company Financial Data Collector",
       program_description="Speed up your grunt work process",
       menu=[{'name': 'Help', 'items': [{
           'type': 'AboutDialog',
           'menuTitle': 'About',
           'name': 'EV Data Reader',
           'description': '',
           'version': '1.0.0',
           'copyright': '2022 TK',
           'developer': 'Taekyu Kim'
        },
           {'type': 'MessageDialog',
            'menuTitle': 'How to use',
            'name': 'How to use',
            'message': ""}
       ]}])
def parse_args():
    """ Use GooeyParser to build up the arguments we will use in our script
    Save the arguments in a default json file so that we can retrieve them
    every time we run the script.
    """
    stored_args = {}
    # get the script name without the extension & use it to build up
    # the json filename
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    args_file = "{}-args.json".format(script_name)
    # Read in the prior arguments as a dictionary
    if os.path.isfile(args_file):
        with open(args_file) as data_file:
            stored_args = json.load(data_file)
    parser = GooeyParser(description='Company Financial Data Collector')
    parser.add_argument('Input_File',
                        action='store',
                        default=stored_args.get('Input_File'),
                        widget='FileChooser',
                        help="Choose the Excel File to read in. Read 'how to use' for specifics.",
                        gooey_options=dict(
                            wildcard="Excel Files (*.xlsx)|*.xlsx", full_width=True
                        ),
                        type=mustBeFile
                        )
    parser.add_argument('Output_Directory',
                        action='store',
                        widget='DirChooser',
                        default=stored_args.get('Output_Directory'),
                        help="Output directory to save collected data file",
                        gooey_options=dict(
                            full_width=True
                        ),
                        type=mustBeDir
                        )
    parser.add_argument('Parameters',
                        action='store',
                        widget='Listbox',
                        help="Parameters you would like to retrieve",
                        nargs="+",
                        gooey_options=dict(
                            full_width=True
                        ),
                        choices=['pricing','range','performance','battery','charging','energy consumption','additional energy consumption','real energy consumption','safety','dimensions and weight','miscellaneous','charge specification']
                        ,
                        default=[
                            ['performance','energy consumption','real energy consumption','charge specification']
                        ]
                        )
    parser.add_argument('-s',
                        '--Maker',
                        help="Enter the name of the maker.",
                        action='store',
                        gooey_options=dict(
                            full_width=True
                        ),
                        default="none"
                        )
                        
    args = parser.parse_args()
    # Store the values of the arguments so we have them next time we run
    with open(args_file, 'w') as data_file:
        # Using vars(args) returns the data as a dictionary
        json.dump(vars(args), data_file)
    return args

# In[]:
def getVehicle(vehicle):
    """retrieves the specific vehicle's data"""
    if vehicle in vehicles:
        loc = vehicles.index(vehicle)
    else:
        raise RuntimeError("There is no such vehicle in the database")
    loc = loc * 2 + 2 - 1
    return pd.concat([allDat[allDat.columns[loc]], allDat[vehicle]], axis=1)

# In[]:
def getCategory(df, category):
    """retrieves all information of the specific category from
    the given dataframe"""
    out = pd.DataFrame({})
    for i in range(0, len(df.columns)-1, 2):
        col1 = df.columns[i]
        col2 = df.columns[i+1]
        sub1 = df[[col1, col2]]
        finders = sub1.loc[sub1.index[sub1[col1] == category].tolist()]
        adder = finders[col2].reset_index(drop=True)
        out = pd.concat([out, adder], axis=1)
    return out

# In[]:
def getMake(maker):
    """retrieves all vehicles from the given maker using getVehicle()"""
    newList = []
    for vehicle in vehicles:
        if maker in vehicle:
            newList.append(vehicle)
    out = pd.DataFrame({})
    for vehicle in newList:
        out = pd.concat([out,getVehicle(vehicle)], axis=1)
    return out 

# In[]:
def saveFile(output, out_directory, category):
    fileName = conf.Input_File
    fileName = os.path.splitext(os.path.basename(fileName))[0]
    outputDir = out_directory + "/" + fileName + "_" + category + ".xlsx"
    output.to_excel(outputDir)

# In[]:
if __name__ == '__main__':
    try:
        conf = parse_args()
    except TypeError as e:
        print("Check your inputs' types and make sure it is an excel file and a folder.", e.args)
        sys.exit(1)
    except ValueError as v:
        print("You need to check your values to see if they are valid.", v.args)
    print("Reading file")
    try:
        allDat = pd.DataFrame(pd.read_excel(conf.Input_File))
        cols = allDat.columns
        vehicles = []
        categories = []
        for i in range(2, len(cols), 2):
            categories.append(i-1)
            vehicles.append(cols[i])
    except RuntimeError as r:
        print(r.args)
    if conf.Maker == 'none' or conf.Maker == "":
        pass
    else:
        allDat = getMake(conf.Maker)
    out = pd.DataFrame({})
    for x in conf.Parameters:
        out = pd.concat([out, getCategory(allDat, x)])
    if conf.Maker != "none" and conf.Maker != "":
        outName = conf.Maker + "_" + "_".join(conf.Parameters) + '.xlsx'
    else:
        outName = "evDataBase_" + "_".join(conf.Parameters) + '.xlsx'
    out.to_excel(conf.Output_Directory + "/" + outName)

