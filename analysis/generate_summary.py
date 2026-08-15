from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
MEDIA_PATH = ROOT / "data" / "media" / "merge_res.json"
PEOPLE_PATH = ROOT / "data" / "people" / "occupations.json"
FIG_DIR = ROOT / "docs" / "figures"
SUMMARY_PATH = ROOT / "docs" / "statistics_summary.json"
STATS_MD_PATH = ROOT / "docs" / "STATISTICS.md"


def clean(value: object) -> str:
    if value is None:
        return "Unknown"
    text = str(value).strip()
    return text if text else "Unknown"


def counter_for(rows: list[dict], key: str) -> Counter:
    return Counter(clean(row.get(key)) for row in rows)


def ordered_bias(counter: Counter) -> list[tuple[str, int]]:
    preferred = ["left", "leftcenter", "center", "rightcenter", "right", "Unknown"]
    result = [(name, counter[name]) for name in preferred if counter[name]]
    used = {name for name, _ in result}
    result.extend(sorted(((k, v) for k, v in counter.items() if k not in used), key=lambda x: (-x[1], x[0])))
    return result


def save_vertical(items: list[tuple[str, int]], title: str, filename: str) -> None:
    labels = [x[0] for x in items]
    values = [x[1] for x in items]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values)
    ax.set_title(title)
    ax.set_ylabel("Records")
    ax.tick_params(axis="x", rotation=25)
    ax.bar_label(bars, padding=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_horizontal(items: list[tuple[str, int]], title: str, filename: str) -> None:
    items = list(reversed(items))
    labels = [x[0] for x in items]
    values = [x[1] for x in items]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(labels, values)
    ax.set_title(title)
    ax.set_xlabel("Records")
    ax.bar_label(bars, padding=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    with MEDIA_PATH.open("r", encoding="utf-8") as f:
        media = json.load(f)
    with PEOPLE_PATH.open("r", encoding="utf-8") as f:
        people = json.load(f)

    bias = counter_for(media, "bias_label_5_class")
    factual = counter_for(media, "factual_reporting")
    credibility = counter_for(media, "credibility_rating")
    occupations = counter_for(people, "occupations")

    bias_items = ordered_bias(bias)
    factual_items = sorted(factual.items(), key=lambda x: (-x[1], x[0]))
    credibility_items = sorted(credibility.items(), key=lambda x: (-x[1], x[0]))
    top_occupations = occupations.most_common(12)

    save_vertical(bias_items, "Political bias labels", "bias_distribution.png")
    save_vertical(factual_items, "Factual reporting", "factual_reporting.png")
    save_vertical(credibility_items, "Credibility rating", "credibility_rating.png")
    save_horizontal(top_occupations, "Top occupations in people dataset", "top_occupations.png")

    wiki_links = sum(bool(clean(row.get("wiki_link")) != "Unknown") for row in media)
    wiki_text = sum(bool(clean(row.get("wiki")) != "Unknown") for row in media)
    domains = {clean(row.get("domain")) for row in media if clean(row.get("domain")) != "Unknown"}

    summary = {
        "media_records": len(media),
        "people_records": len(people),
        "unique_media_domains": len(domains),
        "media_with_wikipedia_link": wiki_links,
        "media_with_wikipedia_text": wiki_text,
        "bias_label_5_class": dict(bias_items),
        "factual_reporting": dict(factual_items),
        "credibility_rating": dict(credibility_items),
        "top_occupations": dict(top_occupations),
    }
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    stats_md = f"""# Dataset statistics

Generated directly from `data/media/merge_res.json` and `data/people/occupations.json`.

- Media records: **{len(media):,}**
- People records: **{len(people):,}**
- Unique media domains: **{len(domains):,}**
- Media records with a Wikipedia link: **{wiki_links:,}**
- Media records with collected Wikipedia text: **{wiki_text:,}**

<table>
<tr>
<td><img src=\"figures/bias_distribution.png\" alt=\"Political bias distribution\"></td>
<td><img src=\"figures/factual_reporting.png\" alt=\"Factual reporting distribution\"></td>
</tr>
<tr>
<td><img src=\"figures/credibility_rating.png\" alt=\"Credibility rating distribution\"></td>
<td><img src=\"figures/top_occupations.png\" alt=\"Top occupations\"></td>
</tr>
</table>

The four figures are generated as separate Matplotlib plots and arranged here as a 2×2 overview.
"""
    STATS_MD_PATH.write_text(stats_md, encoding="utf-8")


if __name__ == "__main__":
    main()
