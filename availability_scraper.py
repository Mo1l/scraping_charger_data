from encodings import utf_8
import pickle
from bitarray import test
import pandas as pd 
import numpy as np
from datetime import datetime
from tqdm import tqdm
from selenium import webdriver
import re
from concurrent.futures import ThreadPoolExecutor
import threading
from selenium.common.exceptions import NoSuchElementException
import os
import geopandas as gpd
import time


def get_availability(input_to_url:list):

    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--incognito")
    options.add_argument("--headless")

    browser = webdriver.Chrome(executable_path="C:\Program Files\Google\ChromeDriver\chromedriver.exe",options=options)

    re_loc = re.compile("&location=*[0-9]*&")
    re_usage = re.compile("[0-9]+/[0-9]+")
    re_at    = re.compile("[0-9]+")

    results = dict()
    for i in input_to_url:
        
        # if I leave lat and lng unknown the page will redirect to the correct coordinates. 
        url  = "https://ladekort.clever.dk/?lat&lng&zoom=7&location=" + str(i) + "&filter=regular,fast,ultra&status=upcoming,available,unavailable,outOfOrder"
        browser.get(url)

        start_time = datetime.now() 
        break_ = True
        #print(i)

        while break_:
            try: 
                if (datetime.now() - start_time).seconds > 15:
                    break_ = False
                    continue
                # This step ensures that the code fails if there is no location card present
                _ = browser.find_element_by_class_name("location-card")
              

                # if location card is found; extract the charger list
                elements = browser.find_elements_by_class_name("charger-list-item")
                
                # If there is no info charger list found - Skip to next - this skips all future charging stations 
                if len(elements) == 0:
                    print("elements is empty")

                #loop over results: 
                results_inner = dict()
                for j,elem in enumerate(elements):
                    
                    charger_usage=elem.find_element_by_class_name("availability").text

                    # I do this step in the case that there is nothing in the charger_usage element it tries another loop 
                    if charger_usage is None: 
                        print("charger_usage is None")

                    # Find the availability string i.e. 0/10 
                    charger_usage= re.search(re_usage, charger_usage)
                    #if charger_usage is None: 
                    #    print(charger_usage)
                    #    print("charger_usage is None")
                    
                                    
                    # extracts 0, 1 from "0/1"
                    charger_usage2 = re.findall(re_at, charger_usage.group(0))

                    charger_avail = charger_usage2[0]
                    charger_total = charger_usage2[1]
                    
                    # Extracts charger type
                    charger_type=elem.find_element_by_class_name("type")
                    charger_type = charger_type.text

                    # Stores in a dict
                    results_inner[charger_type] = [charger_avail, charger_total, datetime.now()]

                # Stores in a dict
                results[i] = results_inner
                break
            except NoSuchElementException: 
            #    if break_:
            #        break
            #    new_url=browser.current_url
            #    #zoom_check=re.search("&zoom=*[0-9]*&", new_url)
            #    loc_check= re.search(re_loc, new_url).group(0)
                
            #    loc_True = (loc_check == "&location&")
            #    if loc_True:
            #        time.sleep(10)
            #        break_ = True
                #time.sleep(0.5)
                pass
            except AttributeError:
                pass
    browser.close()
    return results


def set_up_threads_avail(input_to_url:list, max_workers:int):

    input_ids = np.array_split(input_to_url, max_workers)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(get_availability,    
                            input_ids,
                            timeout = None))


def into_DataFrame(charger_ids:list, avail_list_of_dicts:list):

    avail_dict = {}
    for i, dict_ in enumerate(avail_list_of_dicts):
        avail_dict.update(dict_)

    ids_  = []
    types_ = []
    avails_ = []
    totals_ = []
    datestamps_ = []


    for id in charger_ids:
        try: 
            for type_, value in avail_dict[id].items():
                avail_, total_, datestamp_ = value
                ids_.append(id), types_.append(type_), avails_.append(avail_), totals_.append(total_), datestamps_.append(datestamp_)
        except KeyError:
            ids_.append(id), types_.append(None), avails_.append(None), totals_.append(None), datestamps_.append(datestamp_)

    return pd.DataFrame(list(zip(ids_, types_, avails_, totals_, datestamps_)),columns=["Id", "Charger_type", "Available", "Total", "timestamp"])


def save_DataFrame_to_csv(df:pd.DataFrame, charger_type_:str, some_path):
    now = datetime.now().strftime('%Y%m%d - %H%M%S')
    fname = os.path.join(some_path,"Datascrapes", charger_type_ + now + '.csv')
    df.to_csv(fname, sep=",", encoding='utf_8', date_format='%Y%m%d - %H%M%S')