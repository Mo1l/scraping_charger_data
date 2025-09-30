
import numpy as np
import pandas as pd
from src.scrapertools import request_scraper as Scraper
import json
# load ids to scrape
locations=pd.read_json('./resources/locations_clever.json').T
station_ids=locations['locationId'].tolist()[0:5]

scraper = Scraper.scraper(
    station_ids=station_ids,
    out_path='.',
    url_re='https://clever.dk/api/chargers/location/{}'
)

breakpoint()
# if multithreading - use this
#results_avail=scraper.get_avail_parallel(7)

# instead try: 
# est_urls = ['https://clever.dk/ladekort?location=fdc6fdd8-769d-ed11-aad1-0022489ae94c&zoom=15&filter=standard,fast,rapid&status=available,planned']

# api_call=scraper.scrape_class()
# api_call.run_scrape(0, scraper.urls[0])

results=scraper.get_availability(urls=scraper.urls, silent=False)
breakpoint()

# api_call.run_scrape(0, scraper.urls[1])
# api_call.run_scrape(i=0, scraper.urls[1])

import requests
# response=requests.get(scraper.urls[0:1])
# data=response.json()
# scraper.get_availability(scraper.urls[0:2], silent=False)

# occupation status
# data['availability']['evses']



