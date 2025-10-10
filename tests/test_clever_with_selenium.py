import pandas as pd
from scrapers.with_selenium.scrape_clever_selenium import scraper as Scraper
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

par_results=scraper.run(1)

breakpoint()
