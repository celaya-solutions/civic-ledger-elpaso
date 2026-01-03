Civic Ledger seed pack

Files
- seeds.json: merged with EPWater PSB agendas/minutes roots and sample minutes PDFs
- start_urls.txt: appended with the same URLs
- apply_seed_patch.py: merges these URLs into existing seeds.json/start_urls.txt in-place

Recommended usage
1) Copy apply_seed_patch.py into your repo root (where your seeds.json lives)
2) Run:
   python apply_seed_patch.py --seeds ./seeds.json --start-urls ./start_urls.txt

Then rerun your scraper.
