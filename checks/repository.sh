#!/usr/bin/env bash
set -euo pipefail

python -m py_compile \
  analysis/*.py \
  pipelines/people/*.py \
  pipelines/wikipedia/*.py

python - <<'PY'
import json
from pathlib import Path

required = [
    "README.md",
    "requirements.txt",
    "analysis/generate_summary.py",
    "data/media/merge_res.json",
    "data/people/occupations.json",
    "data/people/statistics/stat_.xlsx",
    "data/people/statistics/occup_stat.xlsx",
    "pipelines/media/parc_medias.ipynb",
    "pipelines/media/parc_arts_medias.ipynb",
    "pipelines/media/parc_arts_allsides.ipynb",
    "notebooks/analysis/build_law_analysis.ipynb",
    "docs/statistics_summary.json",
    "docs/figures/bias_distribution.png",
    "docs/figures/factual_reporting.png",
    "docs/figures/credibility_rating.png",
    "docs/figures/top_occupations.png",
]

for value in required:
    path = Path(value)
    if not path.exists() or path.stat().st_size == 0:
        raise SystemExit(f"missing or empty: {value}")

for value in [
    "data/media/merge_res.json",
    "data/people/occupations.json",
    "docs/statistics_summary.json",
]:
    with Path(value).open("r", encoding="utf-8") as f:
        parsed = json.load(f)
    if not parsed:
        raise SystemExit(f"empty JSON data: {value}")

print("repository check passed")
PY
