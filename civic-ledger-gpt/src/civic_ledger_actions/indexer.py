\
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterator, Any

from .storage import DB, upsert_documents, insert_reddit_items


def iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def build_index(db_path: Path, records_jsonl: Path, reddit_jsonl: Path | None, replace_existing: bool) -> dict[str, int]:
    db = DB(db_path)
    db.init()

    docs_ingested = upsert_documents(db, iter_jsonl(records_jsonl), replace_existing=replace_existing)

    reddit_ingested = 0
    if reddit_jsonl and reddit_jsonl.exists():
        reddit_ingested = insert_reddit_items(db, iter_jsonl(reddit_jsonl))

    return {
        "documents_ingested": docs_ingested,
        "reddit_items_ingested": reddit_ingested,
    }


def cli() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True, help="Path to sqlite db file")
    p.add_argument("--corpus", required=True, help="Path to records.jsonl")
    p.add_argument("--reddit", default=None, help="Optional path to reddit.jsonl")
    p.add_argument("--replace-existing", action="store_true")
    args = p.parse_args()

    out = build_index(
        db_path=Path(args.db),
        records_jsonl=Path(args.corpus),
        reddit_jsonl=Path(args.reddit) if args.reddit else None,
        replace_existing=bool(args.replace_existing),
    )
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    cli()
