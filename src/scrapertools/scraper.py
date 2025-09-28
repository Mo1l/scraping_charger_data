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

class scraper(): 
    """
    A class for scraping charger availability data from a given URL.
    Attributes:
        url_re (function): A callable that generates a URL with variable input.
    Args:
        url_re (function): A function that takes variable input and returns a URL string.
        station_ids: Station ids that are to be scraped. 
    Raises:
        TypeError: If url_re is not a callable function.
    Example:
        my_scraper = scraper(url_re = lambda x: 'url{}'.format(x))
    """
    def __init__(
            self, 
            station_ids:list[str],
            out_path,
            path_for_chromedriver,
            url_re:str='https://ladekort.clever.dk/?lat&lng&zoom=7&location={}&filter=regular,fast,ultra&status=upcoming,available,unavailable,outOfOrder',
        ):
        if not isinstance(url_re, str):
            raise TypeError("url_re must be a str template consisting of an url with variable input")
        self.url_re = url_re
        self.urls = self.construct_urls(station_ids)
        self.out_path = out_path
        self.path_for_chromedriver = path_for_chromedriver

    def construct_urls(self, station_ids):
        self.urls_to_scrape = [self.url_re.format(station_id) for station_id in station_ids] 
        return self.urls_to_scrape 
    
    def get_availability(self,urls, silent=True):

        options = webdriver.ChromeOptions()
        if silent: 
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--incognito")
            options.add_argument("--headless")

        browser = webdriver.Chrome(options=options)

        re_loc = re.compile("&location=*[0-9]*&")
        re_usage = re.compile("[0-9]+/[0-9]+")
        re_at    = re.compile("[0-9]+")

        results = dict()
        for i, url in enumerate(urls):
            
            # if I leave lat and lng unknown the page will redirect to the correct coordinates. 
            browser.get(url)

            start_time = datetime.now() 
            break_ = True

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


    def get_avail_parallel(self, max_workers:int):

        input_ids = np.array_split(self.urls, max_workers)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            return list(executor.map(self.get_availability,    
                                input_ids,
                                timeout = None))


    def into_DataFrame(self, avail_list_of_dicts:list):

        avail_dict = {}
        for i, dict_ in enumerate(avail_list_of_dicts):
            avail_dict.update(dict_)

        ids_  = []
        types_ = []
        avails_ = []
        totals_ = []
        datestamps_ = []


        for id in self.charger_ids:
            try: 
                for type_, value in avail_dict[id].items():
                    avail_, total_, datestamp_ = value
                    ids_.append(id), types_.append(type_), avails_.append(avail_), totals_.append(total_), datestamps_.append(datestamp_)
            except KeyError:
                ids_.append(id), types_.append(None), avails_.append(None), totals_.append(None), datestamps_.append(datestamp_)

        return pd.DataFrame(list(zip(ids_, types_, avails_, totals_, datestamps_)),columns=["Id", "Charger_type", "Available", "Total", "timestamp"])


    def save_DataFrame_to_csv(self, df:pd.DataFrame, charger_type_:str):
        now = datetime.now().strftime('%Y%m%d - %H%M%S')
        fname = os.path.join(self.out_path, f'Datascrapes{charger_type_}{now}.csv')
        df.to_csv(fname, sep=",", encoding='utf_8', date_format='%Y%m%d - %H%M%S')