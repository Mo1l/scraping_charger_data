import pandas as pd
from scrapertools.request_scraper import scraper as Scraper
# load ids to scrape
locations=pd.read_json('./resources/locations_clever.json').T
station_ids=locations['locationId'].tolist()[0:5]

scraper = Scraper(
    station_ids=station_ids,
    out_path='./data/',
    keyword='test',
    url_re='https://clever.dk/api/chargers/location/{}'
)

#breakpoint()
# if multithreading - use this
#results_avail=scraper.get_avail_parallel(7)

# instead try: 
# est_urls = ['https://clever.dk/ladekort?location=fdc6fdd8-769d-ed11-aad1-0022489ae94c&zoom=15&filter=standard,fast,rapid&status=available,planned']

# api_call=scraper.scrape_class()
# api_call.run_scrape(0, scraper.urls[0])

par_results=scraper.run(2)




breakpoint()
