from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import re
from selenium.webdriver.common.by import By
class clever():
    def __init__(self, browser):
        self.re_tools = {'re_loc': re.compile("&location=*[0-9]*&"),
                        're_usage': re.compile("[0-9]+/[0-9]+"),
                        're_at': re.compile("[0-9]+"),
        }
        self.browser = browser
        self.results = {}


    def run_scrape(self, i, url):
        self.browser.get(url)
        start_time = datetime.now() 
        break_ = True

        while break_:
            try: 
                if (datetime.now() - start_time).seconds > 15:
                    break_ = False
                    continue
                # This step ensures that the code fails if there is no location card present
                #_ = self.browser.find_element_by_class_name("location-card")
                _ = self.browser.find_element(By.CLASS_NAME, "location-card")
                

                # if location card is found; extract the charger list
                #elements = self.browser.find_elements_by_class_name("charger-list-item")
                elements = self.browser.find_elements(By.CLASS_NAME, "charger-list-item")
                
                # If there is no info charger list found - Skip to next - this skips all future charging stations 
                if len(elements) == 0:
                    print("elements is empty")

                #loop over results: 
                results_inner = dict()
                for j,elem in enumerate(elements):
                    
                    charger_usage=elem.find_element(By.CLASS_NAME, "availability").text

                    # I do this step in the case that there is nothing in the charger_usage element it tries another loop 
                    if charger_usage is None: 
                        print("charger_usage is None")

                    # Find the availability string i.e. 0/10 
                    charger_usage= re.search(self.re_tools['re_usage'], charger_usage)                    
                                    
                    # extracts 0, 1 from "0/1"
                    charger_usage2 = re.findall(self.re_tools['re_at'], charger_usage.group(0))

                    charger_avail = charger_usage2[0]
                    charger_total = charger_usage2[1]
                    
                    # Extracts charger type
                    charger_type=elem.find_element(By.CLASS_NAME, "type")
                    charger_type = charger_type.text

                    # Stores in a dict
                    results_inner[charger_type] = [charger_avail, charger_total, datetime.now()]
                
                # Stores in a dict
                self.results[i] = results_inner
                break
            except NoSuchElementException: 
            #    if break_:
            #        break
            #    new_url=browser.current_url
            #    #zoom_check=re.search("&zoom=*[0-9]*&", new_url)
            #    loc_check= re.search(re_loc, new_url).group(0)
                
            #    loc_True = (loc_check == "&location&")
            #    if loc_True:
            #        time.sleep(10)
            #        break_ = True
                #time.sleep(0.5)
                pass
            except AttributeError:
                pass
