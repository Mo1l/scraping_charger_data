import availability_scraper as AS
import numpy as np
import os

some_path = "C:\\Users\\glh287\\OneDrive\\Phd\\scraping_charger_data"

Ids_to_scrape=list(map(int, list(np.genfromtxt(os.path.join(some_path,"ultra_ids_to_scrape.csv"), delimiter=','))))

results_avail=AS.set_up_threads_avail(Ids_to_scrape,7)

df=AS.into_DataFrame(Ids_to_scrape, results_avail)

AS.save_DataFrame_to_csv(df, 'ultra', some_path)