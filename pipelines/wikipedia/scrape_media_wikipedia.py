import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT / "data" / "media" / "merge_res.json"
OUTPUT_FILE = ROOT / "data" / "media" / "data_.json"
LOG_FILE = ROOT / "logs" / "wiki_scrape.log"

with INPUT_FILE.open("r", encoding="utf-8") as f:
    datas = json.load(f)

names = []
count = 0
for data in datas:
    count += 1
    print(f"{count}/{len(datas)}")

    if data.get("wiki") != "":
        print("IT is processed")
        continue

    name_ = data["page"]
    names.append(name_.replace(" ", "_"))

    try:
        req = requests.get(data["wiki_link"], timeout=30)
        soup = BeautifulSoup(req.text, "html.parser")
        content = soup.find("div", class_="mw-content-container")
        if content is None:
            raise ValueError("Wikipedia content container not found")

        if "does not have an article" in content.get_text():
            print("DOES not exist")
            continue

        print(data["wiki_link"])
        bio = "".join(d.get_text() for d in soup.find_all("div", class_="mw-body-content"))
        data["wiki"] = bio

        with OUTPUT_FILE.open("w", encoding="utf-8") as f:
            json.dump(datas, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"{e} with {name_}")
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as log_file:
            log_file.write(f"{e} with {name_}\n")
