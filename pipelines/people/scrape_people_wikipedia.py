import json
import time
from pathlib import Path

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver

ROOT = Path(__file__).resolve().parents[2]
OCCUPATIONS_FILE = ROOT / "data" / "people" / "occupations.json"
BUNCH_DIR = ROOT / "data" / "people" / "bunchs"


def create_bunchs_from_json(json_file: Path) -> None:
    with json_file.open("r", encoding="utf-8") as f:
        datas = json.load(f)

    bunch_size = 10
    BUNCH_DIR.mkdir(parents=True, exist_ok=True)

    for i in range(0, len(datas), bunch_size):
        datas_bunch = datas[i : i + bunch_size]
        with (BUNCH_DIR / f"{i // bunch_size}.json").open("w", encoding="utf-8") as fp:
            json.dump(datas_bunch, fp, indent=2, ensure_ascii=False)


def parc_wiki_trough_google_request() -> None:
    for file_path in sorted(BUNCH_DIR.glob("*.json")):
        try:
            with file_path.open("r", encoding="utf-8") as f:
                datas = json.load(f)
            for item in datas:
                item["num_file"] = file_path.stem
        except Exception:
            print(f"Failed to read {file_path}")
            continue

        google_url = "https://www.google.com/search?q=wikipedia"
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"user-agent={UserAgent().random}")

        datas_new = []
        field_for_req = "name"

        for data in datas:
            name = data[field_for_req]
            if data.get("wiki_link") or data.get("wiki"):
                print(f"{name} is ALREADY PROCESSED")
                datas_new.append(data)
                with file_path.open("w", encoding="utf-8") as f:
                    json.dump(datas_new, f, indent=2, ensure_ascii=False)
                continue

            driver = webdriver.Chrome(options=options)
            try:
                search_url = google_url + " " + name.replace(" ", "+")
                driver.get(search_url)
                time.sleep(5)
                soup = BeautifulSoup(driver.page_source, "html.parser")

                link_wiki = ""
                for link in soup.find_all("a"):
                    href = link.get("href")
                    if href and "https://en.wikipedia.org/wiki/" in href:
                        link_wiki = href
                        break

                data["wiki_link"] = link_wiki
                datas_new.append(data)
                with file_path.open("w", encoding="utf-8") as f:
                    json.dump(datas_new, f, indent=2, ensure_ascii=False)
            finally:
                driver.quit()


if __name__ == "__main__":
    create_bunchs_from_json(OCCUPATIONS_FILE)
    # parc_wiki_trough_google_request()
