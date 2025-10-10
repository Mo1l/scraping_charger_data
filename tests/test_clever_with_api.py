import pandas as pd
from scrapers.with_requests.scrape_availability_with_api import scraper as Scraper
# load ids to scrape
locations=pd.read_json('./resources/locations_clever.json').T
station_ids=locations['locationId'].tolist()[0:3]

from scrapers.with_requests.scrape_availability_with_api import scraper as Scraper
scraper = Scraper(
    identifiers=station_ids,
    out_path='./data/',
    keyword='test',
    url_re='https://clever.dk/api/chargers/location/{}'
)
par_results=scraper.run(1)

from scrapers.with_requests.scrape_locations_with_api import scraper as Scraper
scraper = Scraper(
    identifiers=['locations'],
    out_path='./data/',
    keyword='test',
    url_re='https://clever.dk/api/chargers/locations'
)
breakpoint()
par_results=scraper.run(1)
par_results

breakpoint()
