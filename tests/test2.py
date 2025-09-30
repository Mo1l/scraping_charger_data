
import numpy as np
from src.scrapertools import scraper as Scraper
from src.scrape_scripts.scrape_clever_from_url import clever 
# load ids to scrape
station_ids=list(
    map(int, 
        list(
            np.genfromtxt(
                './ids_to_scrape/ultra_ids_to_scrape.csv', 
                delimiter=',')
            )
    )
)

scraper = Scraper.scraper(station_ids = station_ids, 
                  out_path = '.',
                  path_for_chromedriver = "C:\Program Files\Google\ChromeDriver\chromedriver.exe",
                  scrape_class=clever,
                  url_re='https://ladekort.clever.dk/?lat&lng&zoom=7&location={}&filter=regular,fast,ultra&status=upcoming,available,unavailable,outOfOrder'
)

# if multithreading - use this
#results_avail=scraper.get_avail_parallel(7)

# instead try: 
test_urls = ['https://clever.dk/ladekort?location=fdc6fdd8-769d-ed11-aad1-0022489ae94c&zoom=15&filter=standard,fast,rapid&status=available,planned']


scraper.get_availability(test_urls, silent=False)

