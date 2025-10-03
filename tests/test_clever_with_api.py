import pandas as pd
from scrapers.scrape_clever_with_api import scraper as Scraper
# load ids to scrape
locations=pd.read_json('./resources/locations_clever.json').T
station_ids=locations['locationId'].tolist()[0:50]

scraper = Scraper(
    station_ids=station_ids,
    out_path='./data/',
    keyword='test',
    url_re='https://clever.dk/api/chargers/location/{}'
)

par_results=scraper.run(1)

breakpoint()
