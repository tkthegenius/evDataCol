from __future__ import print_function

import os
import os.path
import pandas as pd
import datetime
import json
import time
import requests

from bs4 import BeautifulSoup
from main import createDataBase
from gooey import Gooey, GooeyParser

URL = "https://ev-database.org/#sort:path~type~order=.rank~number~desc|range-slider-range:prev~next=0~1200|range-slider-acceleration:prev~next=2~23|range-slider-topspeed:prev~next=110~450|range-slider-battery:prev~next=10~200|range-slider-towweight:prev~next=0~2500|range-slider-fastcharge:prev~next=0~1500|paging:currentPage=0|paging:number=9"


@Gooey(program_name="EV Database Generator",
       program_description="The world of EV data in your desktop",
       menu=[{'name': 'Help', 'items': [{
           'type': 'AboutDialog',
           'menuTitle': 'About',
           'name': 'EV Database Generator',
           'description': 'Accelerated EV data collector',
           'version': '2.0.0',
           'copyright': '2022 TK',
           'developer': 'Taekyu Kim'
       },
           {'type': 'MessageDialog',
            'menuTitle': 'How to use',
            'name': 'How to use',
            'message': "Input the directory you want your information in and click the start button."}
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
    parser.add_argument('Output_Directory',
                        action='store',
                        widget='DirChooser',
                        default=stored_args.get('Output_Directory'),
                        help="Output directory to save collected data file",
                        gooey_options=dict(
                            full_width=True
                        )
                        )
    parser.add_argument('-s',
                        '--startpoint',
                        help="Enter the startpoint of the list. 0 is the beginning. Pick a number between 0 and 100.",
                        action='store',
                        gooey_options=dict(
                            full_width=True
                        ),
                        default=0
                        )
    args = parser.parse_args()
    # Store the values of the arguments so we have them next time we run
    with open(args_file, 'w') as data_file:
        # Using vars(args) returns the data as a dictionary
        json.dump(vars(args), data_file)
    return args


def save_results(collected_data, output):
    """ save created financial data dataframe into selected folder for output
    """
    now = datetime.datetime.now()
    dateNTime = now.strftime("%Y%m%d_%H%M%S")
    # collected_data = collected_data.reset_index()
    outputFileDir = output + "/" + dateNTime + "_evDatabase.xlsx"
    collected_data.to_excel(outputFileDir)


if __name__ == '__main__':
    conf = parse_args()
    print("Reading webpage")
    print("Retrieving and saving requested data")
    page = requests.get(URL)
    soupTemp = BeautifulSoup(page.text, 'html.parser')
    cars = soupTemp.findAll('div', {'class': 'title-wrap'})
    titles = []
    ids = []
    for x in cars:
        titles.append(x.find('a', {'class': 'title'}).text)
        ids.append(x.find('a', {'class': 'title'})['href'])

    outputFile = pd.DataFrame({})

    startpoint = int(conf.startpoint)
    endpoint = (startpoint + 50) % len(ids)

    for i in range(startpoint, endpoint, 1):
        newURL = "https://ev-database.org" + ids[i]
        try:
            adder = createDataBase(newURL)
            adder.reset_index(inplace=True)
            outputFile = pd.concat([outputFile, adder], axis=1, sort=False)
            print("sleeping for 100 seconds.............")
            time.sleep(100)
        except ConnectionError as e:
            print(e.args)
            break
        except:
            pass

    dataAdded = len(outputFile.columns)
    print("added ", int(dataAdded/2),
          " vehicles to the database out of ", len(ids))
    save_results(outputFile, conf.Output_Directory)
    print("Done")
