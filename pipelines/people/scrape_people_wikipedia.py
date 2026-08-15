import json
import os
import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
import os

def create_bunchs_from_json(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        datas = json.load(f)

    bunch_size = 10

    if not os.path.exists("bunchs"):
        os.makedirs("bunchs")

    for i in range(0, len(datas), bunch_size):
        datas_bunch = datas[i:i+bunch_size]
        with open(f"bunchs/{i//bunch_size}.json", "w", encoding="utf-8") as fp:
            json.dump(datas_bunch, fp, indent=2) 

def parc_wiki_trough_google_request():
    path = "bunchs"
    for filename in os.listdir(path): 
        try:
            with open(f"{path}/{filename}", "r", encoding="utf-8") as f:
                datas = json.load(f)
            for item in datas:
                item["num_file"] = filename.replace(".json", "")    
        except Exception as e:
            print("Failed to read the file.")
            with open(f"{path}/{filename}", "r", encoding="utf-8") as f:
                f.seek(0, 2)
                f.seek(max(f.tell() - 10, 0), 0)
                last_chars = f.read()
                print("Last 10 characters:", last_chars)
        
        names = []
        google_url = "https://www.google.com/search?q=wikipedia"
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        ua = UserAgent()
        user_agent = ua.random
        options.add_argument(f'user-agent={user_agent}')

        datas_new = []
         
        field_for_req = "name" 

        for data in datas:
            print(data["num_file"])
            name = data[field_for_req]
            if(data.get("wiki_link") is not None or data.get("wiki") is not None):
                print(f"{name} is ALREADY PROCESSED")
                datas_new.append(data)
                with open(f"{path}/{filename}", "w", encoding="utf-8") as f:
                    print("with " + data[field_for_req])
                    json.dump(datas_new, f, indent=2)
                continue
            driver = webdriver.Chrome(options=options)
            try: 
                name = name.replace(" ", "+")
                names.append(name)

                search_url = google_url + " " + name

                driver.get(search_url)
                time.sleep(5)  # Wait for page to load

                soup = BeautifulSoup(driver.page_source, "html.parser")
                links_ = soup.find_all("a")
                link_wiki = str()
                for l_ in links_:
                    href = l_.get("href")

                    if href != None and "https://en.wikipedia.org/wiki/" in href:
                        link_wiki = href
                        print(href)
                        
                        break
                data["wiki_link"] = link_wiki

                datas_new.append(data)
                
                with open(f"{path}/{filename}", "w", encoding="utf-8") as f:
                    print("with " + data["page"] + " : " + link_wiki)
                    json.dump(datas_new, f, indent=2)
                
            except:
                driver.quit()
                continue
            driver.quit()                       

create_bunchs_from_json("occupations.json")            
            
#parc_wiki_trough_google_request()            