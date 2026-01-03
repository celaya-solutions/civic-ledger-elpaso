#!/usr/bin/env bash
set -euo pipefail

DB=./civic_ledger.sqlite

civic-ledger-build-index --corpus ./data/records.jsonl --reddit ./data/reddit.jsonl --db $DB
civic-ledger-api --db $DB --host 127.0.0.1 --port 8787
