from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import re
import requests
import numpy as np
#from selenium.webdriver.common.by import By
class clever():
    def __init__(self, silent):
        self.results = {}
    #     self.__setup__(silent)

    # def __setup__(self, silent):
    #     """
    #     The setup file is constructed to 
    #     """

    def run_scrape(self, i, url):
        response=requests.get(url)
        request_time = datetime.now() 
        
        # 
        data=response.json()

        # Get locationId
        locationId=data['locationId'] 
        
        # Create aggreate data
        chargepointIds=data['evses']
        nchargepoints = len(chargepointIds.keys())
        availability=data['availability']['evses']
        navailable=np.array([availability[cid]['status']=='Available' for cid in chargepointIds.keys()]).sum(dtype=int)

        # data set one:
        self.results[locationId] = {
            'locationId': locationId,
            'request_time': request_time.isoformat(),
            'navailable': int(navailable), 
            'ntotal': int(nchargepoints), 
            'data': data,
        }

