import pandas as pd
from scrapers.scrape_clever_selenium import scraper as Scraper
# load ids to scrape
locations=pd.read_json('./resources/locations_clever.json').T
station_ids=locations['locationId'].tolist()[0:5]

scraper = Scraper(
    station_ids=station_ids,
    out_path='./data/',
    keyword='test',
    url_re='https://clever.dk/ladekort?lat=55.674701&lng=12.506551&zoom=15&location={}&filter=standard,fast,rapid&status=available,planned',
    silent=False,
)

#breakpoint()
# if multithreading - use this
#results_avail=scraper.get_avail_parallel(7)

# instead try: 
# est_urls = ['https://clever.dk/ladekort?location=fdc6fdd8-769d-ed11-aad1-0022489ae94c&zoom=15&filter=standard,fast,rapid&status=available,planned']

# api_call=scraper.scrape_class()
# api_call.run_scrape(0, scraper.urls[0])

par_results=scraper.run(1)




breakpoint()
