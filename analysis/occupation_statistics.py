import json
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "people" / "occupations.json"
OUTPUT_FILE = ROOT / "data" / "people" / "statistics" / "stat_.xlsx"

with INPUT_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)

counts = Counter(item.get("occupations") or "Unknown" for item in data)
df = pd.DataFrame.from_dict(counts, orient="index", columns=["Count"]).sort_values("Count", ascending=False)
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_excel(OUTPUT_FILE, index_label="Occupations")
