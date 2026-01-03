from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCHEMA_SQL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS documents (
  document_id TEXT PRIMARY KEY NOT NULL,
  url TEXT,
  canonical_url TEXT,
  title TEXT,
  content_type TEXT,
  out_path TEXT,
  published_at TEXT,
  fetched_at TEXT,
  http_status INTEGER,
  sha256_text TEXT,
  text TEXT
);

CREATE TABLE IF NOT EXISTS reddit_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  keyword TEXT,
  title TEXT,
  subreddit TEXT,
  permalink TEXT,
  url TEXT,
  created_utc REAL,
  score INTEGER,
  num_comments INTEGER,
  selftext TEXT
);

CREATE INDEX IF NOT EXISTS idx_documents_url ON documents(url);
CREATE INDEX IF NOT EXISTS idx_documents_title ON documents(title);
CREATE INDEX IF NOT EXISTS idx_reddit_keyword ON reddit_items(keyword);
"""


@dataclass(frozen=True)
class DB:
    path: Path

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.path))
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()


def upsert_documents(db: DB, docs: Iterable[dict[str, Any]], replace_existing: bool = False) -> int:
    sql_upsert = """
    INSERT INTO documents (
      document_id, url, canonical_url, title, content_type, out_path,
      published_at, fetched_at, http_status, sha256_text, text
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(document_id) DO UPDATE SET
      url=excluded.url,
      canonical_url=excluded.canonical_url,
      title=excluded.title,
      content_type=excluded.content_type,
      out_path=excluded.out_path,
      published_at=excluded.published_at,
      fetched_at=excluded.fetched_at,
      http_status=excluded.http_status,
      sha256_text=excluded.sha256_text,
      text=excluded.text
    """
    sql_replace = """
    INSERT OR REPLACE INTO documents (
      document_id, url, canonical_url, title, content_type, out_path,
      published_at, fetched_at, http_status, sha256_text, text
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    n = 0
    with db.connect() as conn:
        cur = conn.cursor()
        for d in docs:
            url = d.get("url") or ""
            document_id = d.get("document_id") or ""
            if not document_id:
                document_id = hashlib.sha256(url.encode("utf-8")).hexdigest()
            row = (
                document_id,
                url,
                d.get("canonical_url"),
                d.get("title"),
                d.get("content_type"),
                d.get("out_path"),
                d.get("published_at"),
                d.get("fetched_at"),
                d.get("http_status"),
                d.get("sha256_text"),
                d.get("text") or "",
            )
            cur.execute(sql_replace if replace_existing else sql_upsert, row)
            n += 1
        conn.commit()
    return n


def insert_reddit_items(db: DB, items: Iterable[dict[str, Any]], replace_existing: bool = False) -> int:
    # no stable id in input; append-only
    sql = """
    INSERT INTO reddit_items (
      keyword, title, subreddit, permalink, url, created_utc, score, num_comments, selftext
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    n = 0
    with db.connect() as conn:
        cur = conn.cursor()
        for item in items:
            kw = item.get("keyword")
            it = item.get("item") or {}
            cur.execute(sql, (
                kw,
                it.get("title"),
                it.get("subreddit"),
                it.get("permalink"),
                it.get("url"),
                it.get("created_utc"),
                it.get("score"),
                it.get("num_comments"),
                it.get("selftext"),
            ))
            n += 1
        conn.commit()
    return n


def count_documents(db: DB) -> int:
    with db.connect() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0])
