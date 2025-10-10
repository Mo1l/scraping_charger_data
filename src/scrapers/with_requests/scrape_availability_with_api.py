from selenium.common.exceptions import NoSuchElementException
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
            identifiers,
            out_path,
            url_re:str={},
            silent=True):
        # Simply calls the Base init function.
        super().__init__(
            keyword=keyword,
            identifiers=identifiers,
            out_path=out_path, 
            url_re=url_re,
            silent=silent,)

        self.results = {}
        self.__setup__(silent)

    def __setup__(self, silent):
        """
        The setup is part of the initialization of the class
        and should include any preliminaries before querying the first 
        url. 
        If Selenium is used it includes setting up the browser object.
        If requests is used it can simply be empty.
        """
        pass
    
    #@profile
    def query_url(self, url, scraper_tools):
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

        result ={
            'locationId': locationId,
            'request_time': request_time.isoformat(),
            'navailable': int(navailable), 
            'ntotal': int(nchargepoints), 
            'data': data,
        }

        # return 
        return result
