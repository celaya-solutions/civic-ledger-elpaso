#!/usr/bin/env python3
"""Apply Civic Ledger seed patch in-place.

Usage:
  python apply_seed_patch.py --seeds ./seeds.json --start-urls ./start_urls.txt
"""
import argparse, json
from pathlib import Path

NEW_SEED_URLS = [
  "https://www.epwater.org/about-us/public-service-board/psb-agendas-minutes",
  "https://www.epwater.org/about-us/public-service-board",
  "https://www.epwater.org/about-us/public-service-board/view-live-psb-meetings",
  "https://www.epwater.org/ep-water/assets/files/meetings/137/minutes-october-8-2025-1.pdf",
  "https://www.epwater.org/ep-water/assets/files/meetings/136/minutes-september-10-2025-2.pdf",
  "https://www.epwater.org/ep-water/assets/files/meetings/135/item-01-minutes-august-13-2025.pdf",
  "https://donaanaconm.portal.civicclerk.com/",
  "https://www.donaana.gov/government/agendas/index.php",
]

RSS_ADD = [
  "EPWater Public Service Board agendas minutes",
  "EPWater rate increase water rates fees",
  "EPWater large customer water use",
  "El Paso data center water demand EPWater",
]

REDDIT_ADD = [
  "EPWater",
  "Public Service Board",
  "PSB agenda",
  "EPWater minutes",
  "EPWater rates",
]

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument("--seeds", default="seeds.json")
  ap.add_argument("--start-urls", default="start_urls.txt")
  args = ap.parse_args()

  seeds_path = Path(args.seeds)
  start_path = Path(args.start_urls)

  obj = json.loads(seeds_path.read_text())
  obj.setdefault("seed_urls", [])
  obj.setdefault("google_news_rss_queries", [])
  obj.setdefault("reddit_keywords", [])

  def merge_unique(lst, items):
    s = set(lst)
    for it in items:
      if it not in s:
        lst.append(it)
        s.add(it)

  merge_unique(obj["seed_urls"], NEW_SEED_URLS)
  merge_unique(obj["google_news_rss_queries"], RSS_ADD)
  merge_unique(obj["reddit_keywords"], REDDIT_ADD)

  seeds_path.write_text(json.dumps(obj, indent=2))

  existing = []
  if start_path.exists():
    existing = start_path.read_text().splitlines()
  s = set(existing)
  with start_path.open("a") as f:
    for u in NEW_SEED_URLS:
      if u not in s:
        f.write(u + "\n")
        s.add(u)

  print("seed_urls:", len(obj["seed_urls"]))
  print("start_urls:", len(s))

if __name__ == "__main__":
  main()
