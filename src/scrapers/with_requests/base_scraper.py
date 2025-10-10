from abc import ABC, abstractmethod

from encodings import utf_8
import pickle
import pandas as pd 
import numpy as np
from datetime import datetime
from tqdm import tqdm
from selenium import webdriver
import requests
import re
from concurrent.futures import ThreadPoolExecutor
import threading
import os
import json

class base_scraper(ABC): 
    """
    An Abstract class that provides the barebone methods needed to perform a scrape.
    It also specifies methods that has to be defined within the inherited class object. (see @abstractmethod @property) 
    Attributes:
        url_re (function): A callable that generates a URL with variable input.
    Args:
        url_re (function): A function that takes variable input and returns a URL string.
        identifiers: identifiers that identify object to be scraped 
    Raises:
        TypeError: If url_re is not a callable function.
    Example:
        my_scraper = scraper(url_re = lambda x: 'url{}'.format(x))
    """
    def __init__(
            self, 
            keyword,
            identifiers:list[str],
            out_path,
            silent:bool=True,
            url_re:str='{}',
        ):
        if not isinstance(url_re, str):
            raise TypeError("url_re must be a str template consisting of an url with variable input")
        if not isinstance(keyword, str): 
            raise TypeError("keyword must be a str. Give it a name that specifies ")
        
        self.url_re = url_re
        self.identifiers = identifiers
        self.urls = self.construct_urls(identifiers)
        self.identifiers_urls = dict(zip(identifiers, self.construct_urls(identifiers)))
        self.out_path = out_path
        self.keyword = keyword
        self.silent = silent

    @property
    @abstractmethod
    def __setup__(self, silent):
        """
        Should contain anything that has to be performed before running the scrape,
        and should be stored in a scraper_tools dict and returned 
        if Requests is used: Can be empty
        if Selenium is used: Setup of the browser. 
        """
        scraper_tools = {}
        return scraper_tools

    @property
    @abstractmethod
    def query_url(self, url, scraper_tools):
        """
        Should contain the commands to be performed to either manipulate selenium browser object or 
        request calls
        """
        pass  

    def construct_urls(self, identifiers):
        self.urls_to_scrape = [self.url_re.format(identifier) for identifier in identifiers] 
        return self.urls_to_scrape 
    
    def query_urls(self, identifiers):
        """
        Fetches requested data from the `.run_scrape()` script for a list of URLs by executing the scraping logic for each URL.
        `.__setup__()`is used here to initialize any needed scrape objects.
        Args:
            identifiers (list): A list of identifiers that can be mapped to an URL through self.identifiers_urls
             to scrape for information.
        Returns:
            dict: A dictionary mapping each locationId to its corresponding scrape result.
        Notes:
            - This method creates a local results dictionary to support parallel processing.
            - Only the wrapper method `.run()` stores results to `self.results`.
            - Each URL is processed by calling `self.run_scrape(i=i, url=url)`, which should ALWAYS return a tuple of (locationId, result).
            - the content of (locationId, result) can vary across the different inherited classes.
        """
        # performing preliminaries for scraping: 
        scraper_tools=self.__setup__(self.silent)

        results = {}
        for identifier in identifiers:
            url = self.identifiers_urls[identifier]
            result=self.query_url(url=url, scraper_tools=scraper_tools)
            results[identifier] = result
        return results

    def query_urls_parallel(self, max_workers:int):
        """
        runs `.query_urls()` in parallel.
        Args:
            max_workers (int): The maximum number of worker threads to use for parallel processing.
        Returns:
            dict: A dictionary mapping station identifiers to their availability status.
        Notes:
            - The method uses `self.get_availability` to fetch availability for each subset of URLs.
            - Results from all threads are flattened into a single dictionary.
        """

        input_ids = np.array_split(self.identifiers, max_workers)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results_workers=list(executor.map(self.query_urls,    
                                input_ids,
                                timeout = None))
            # flattening results and returning
            return {k: v for results_worker in results_workers for k, v in results_worker.items()}


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

    def dump_as_json(self, results):
        now = datetime.now().strftime('%Y%m%d-%H%M%S')
        fname = os.path.join(self.out_path, f"scrape_results_{self.keyword}_{now}.json")
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
    

    def run(self,max_workers:int=1):
        if not isinstance(max_workers, int):
            raise ValueError(f'max_worker is of type {type(max_workers)}. Should be Int.')
        # scrape:
        if max_workers== 1:
            results=self.query_urls(self.identifiers)
        else: 
            results=self.query_urls_parallel(max_workers=max_workers)
            pass
        
        # stores within results 
        self.results = results
        
        # dumps as json
        self.dump_as_json(results)
