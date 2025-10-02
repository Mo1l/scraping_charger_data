from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from selenium import webdriver
from datetime import datetime
import re
import requests
import numpy as np
from .base_scraper import base_scraper as Base
#from selenium.webdriver.common.by import By
class scraper(Base):
    def __init__(
            self, 
            keyword,
            station_ids,
            out_path,
            url_re:str={},
            silent=True):
        # Simply calls the Base init function.
        super().__init__(
            keyword=keyword,
            station_ids=station_ids,
            out_path=out_path, 
            url_re=url_re,
            silent=silent,)

        self.results = {}

        self.re_tools = {'re_loc': re.compile("&location=*[0-9]*&"),
                're_usage': re.compile("[0-9]+/[0-9]+"),
                're_at': re.compile("[0-9]+"),
}


    def __setup__(self, silent):
        """
        The setup is part of the initialization of the class
        and should include any preliminaries before querying the first 
        url. 
        If Selenium is used it includes setting up the browser object.
        If requests is used it can simply be empty.
        """
        options = webdriver.ChromeOptions()
        if silent: 
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--incognito")
            options.add_argument("--headless")

        browser = webdriver.Chrome(options=options)
        scraper_tools = {'browser': browser}
        return scraper_tools

    def run_scrape(self, i, url, scraper_tools):
        # Unpacks scraper_tools 
        browser=scraper_tools['browser']
        browser.get(url)
        start_time = datetime.now() 
        break_ = True
        while break_:
            try: 
                if (datetime.now() - start_time).seconds > 15:
                    break_ = False
                    continue
                # This step ensures that the code fails if there is no location card present
                #_ = browser.find_element_by_class_name("location-card")
                _ = browser.find_element(By.CLASS_NAME, "location-card")
                
                # if location card is found; extract the charger list
                #elements = browser.find_elements_by_class_name("charger-list-item")
                elements = browser.find_elements(By.CLASS_NAME, "charger-list-item")
                
                # If there is no info charger list found - Skip to next - this skips all future charging stations 
                if len(elements) == 0:
                    print("elements is empty")

                #loop over results: 
                results_inner = dict()
                for j,elem in enumerate(elements):
                    
                    charger_usage=elem.find_element(By.CLASS_NAME, "availability").text

                    # I do this step in the case that there is nothing in the charger_usage element it tries another loop 
                    if charger_usage is None: 
                        print("charger_usage is None")

                    # Find the availability string i.e. 0/10 
                    charger_usage= re.search(self.re_tools['re_usage'], charger_usage)                    
                                    
                    # extracts 0, 1 from "0/1"
                    charger_usage2 = re.findall(self.re_tools['re_at'], charger_usage.group(0))

                    charger_avail = charger_usage2[0]
                    charger_total = charger_usage2[1]
                    
                    # Extracts charger type
                    charger_type=elem.find_element(By.CLASS_NAME, "type")
                    charger_type = charger_type.text

                    # Stores in a dict
                    results_inner[charger_type] = [charger_avail, charger_total, datetime.now().isoformat()]

                # Stores in a dict
                #self.results[i] = results_inner
                return i, results_inner
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
