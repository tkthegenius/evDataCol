from __future__ import print_function

import os
import os.path
import sys
import pandas as pd 
import json

from gooey import Gooey, GooeyParser

@Gooey(program_name="Company Financial Data Collector",
       program_description="Speed up your grunt work process",
       menu=[{'name': 'Help', 'items': [{
           'type': 'AboutDialog',
           'menuTitle': 'About',
           'name': 'Financial Data Collector',
           'description': 'Accelerate your data research process so you can move on from the grunt work',
           'version': '1.2.0',
           'copyright': '2021 TK',
           'developer': 'Taekyu Kim'
       },
           {'type': 'MessageDialog',
            'menuTitle': 'How to use',
            'name': 'How to use',
            'message': "Input an excel file with company names and stock Tickers to retrieve financial datum of your choice. The first column must be titled 'Name', ane the second must be 'Code'."}
       ]}])

def mustBeFile(pathway):
    if os.path.isfile(pathway):
        return pathway
    else:
        raise TypeError(
            "What you provided is not a directory. Please enter a valid file")

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
    parser.add_argument('Parameters',
                        action='store',
                        widget='Listbox',
                        help="Parameters you would like to retrieve",
                        nargs="+",
                        gooey_options=dict(
                            full_width=True
                        ),
                        choices=[
                            'pricing','range','performance','efficiency'
                 
                        ],
                        default=[
                       
                        ]
                        )
    parser.add_argument('-s',
                        '--Sheet_Name',
                        help="Enter the name of the sheet EXACTLY. If there is only one sheet, input 'none' or don't input anything.",
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


def combine_files(src_directory):
    """ Read in source excel file and create
    data frame to retrieve target companies
    """
    if conf.Sheet_Name == 'none':
        all_Data = pd.DataFrame(pd.read_excel(src_directory))
    else:
        try:
            all_Data = pd.DataFrame(pd.read_excel(
                src_directory, sheet_name=conf.Sheet_Name))
        except RuntimeError as r:
            print(r.args)
    if 'Code' not in all_Data.keys():
        raise RuntimeError("this sheet does not contain the column'Code'")
    specific_Data = all_Data[all_Data['Code'].notnull()]

    return specific_Data

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
        sales_df = combine_files(conf.Input_File)
    except RuntimeError as r:
        print(r.args)
    codes = sales_df['Code']
    names = sales_df['Name']
    nameDf = pd.DataFrame(names).reset_index()
    nameDf = nameDf.loc[:, ['Name']]
    outputFile = pd.DataFrame(columns=conf.Parameters)
    print("Retrieving and saving requested data")
    
    print("Done")
