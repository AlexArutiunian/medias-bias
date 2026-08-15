import json
import pandas as pd

res = {}

with open("occupations.json", "r", encoding="utf-8") as f:
    datas = json.load(f)
    for data in datas:
        label = data["occupations"]
        if label not in res:
            res[label] = 1
        else:
            res[label] += 1
df = pd.DataFrame.from_dict(res, orient="index", columns=["Count"])

df.to_excel("stat_.xlsx", index_label="Occupations")