
#breakpoint()
#import scraper-tool 
import numpy as np
from src.scrapertools import scraper as Scraper

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
                  url_re='https://ladekort.clever.dk/?lat&lng&zoom=7&location={}&filter=regular,fast,ultra&status=upcoming,available,unavailable,outOfOrder'
)
breakpoint()

# if multithreading - use this
#results_avail=scraper.set_up_threads_avail(7)

# instead try: 
scraper.get_availability(scraper.urls)

df=scraper.into_DataFrame(Ids_to_scrape, results_avail)

AS.save_DataFrame_to_csv(df, 'ultra')
