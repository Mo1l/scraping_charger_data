from encodings import utf_8
import pickle
from bitarray import test
import pandas as pd 
import numpy as np
from datetime import datetime
from tqdm import tqdm
from selenium import webdriver
import requests
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
            scrape_class, 
            url_re:str='https://ladekort.clever.dk/?lat&lng&zoom=7&location={}&filter=regular,fast,ultra&status=upcoming,available,unavailable,outOfOrder',
        ):
        if not isinstance(url_re, str):
            raise TypeError("url_re must be a str template consisting of an url with variable input")
        self.url_re = url_re
        self.urls = self.construct_urls(station_ids)
        self.out_path = out_path
        self.path_for_chromedriver = path_for_chromedriver
        self.scrape_class = scrape_class

    def construct_urls(self, station_ids):
        self.urls_to_scrape = [self.url_re.format(station_id) for station_id in station_ids] 
        return self.urls_to_scrape 
    
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