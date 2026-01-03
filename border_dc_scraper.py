#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urljoin, urldefrag, urlparse

import feedparser
import requests
import tldextract
import trafilatura
from bs4 import BeautifulSoup
from dateutil import parser as dtparser
from pypdf import PdfReader
from pdfminer.high_level import extract_text as pdfminer_extract_text
from youtube_transcript_api import YouTubeTranscriptApi

UA = "BorderDCScraper/1.0 (+local research; respects robots.txt; contact: you)"
DEFAULT_DELAY_S = 1.2

SEED_URLS = [
    # Doña Ana County project page + meeting packets
    "https://www.donaana.gov/about_us/economic_development_projects.php",
    "https://donaanaconm.portal.civicclerk.com/event/684/files/agenda/3873",
    "https://donaanaconm.portal.civicclerk.com/event/708/files",

    # Source NM tag page (rolls up Project Jupiter coverage)
    "https://sourcenm.com/tag/project-jupiter/",

    # NM Environmental Law Center press release + PDF
    "https://nmelc.org/2025/10/24/local-community-sues-dona-ana-county-to-stop-billions-of-tax-dollars-going-to-openai-data-center/",
    "https://nmelc.org/wp-content/uploads/2025/10/PR-SP_ST-10-23-25.pdf",

    # Complaint PDF mirror
    "https://www.courthousenews.com/wp-content/uploads/2025/10/empowerment-congress-v-county-of-dona-ana-complaint.pdf",

    # NMED air permit coverage (News From The States mirror)
    "https://www.newsfromthestates.com/article/nmed-says-data-center-project-jupiters-air-quality-applications-incomplete-now",

    # Local reporting examples (add more as you find them)
    "https://kfoxtv.com/newsletter-daily/community-group-sues-dona-ana-county-commissioners-over-project-jupiter-approval",
    "https://spectrumlocalnews.com/tx/austin/news/2025/11/24/meta-data-center-in-east-el-paso-concerns-local-residents",

    # YouTube short (El Paso Matters clip)
    "https://www.youtube.com/shorts/h47NsLc0mOw",
]

GOOGLE_NEWS_RSS_QUERIES = [
    "Project Jupiter Santa Teresa data center",
    "Doña Ana County Project Jupiter industrial revenue bonds",
    "Meta data center El Paso water concerns",
    "El Paso data center resident concerns",
]

REDDIT_KEYWORDS = [
    "Project Jupiter",
    "Santa Teresa data center",
    "Doña Ana County industrial revenue bonds",
    "Meta data center El Paso",
    "El Paso data center water",
]

@dataclass
class Record:
    id: str
    url: str
    canonical_url: str
    fetched_at: str
    content_type: str
    http_status: int
    title: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[str] = None
    text: Optional[str] = None
    lang: Optional[str] = None
    sha256_text: Optional[str] = None
    out_path: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[list] = None

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def norm_url(u: str) -> str:
    u = u.strip()
    u, _frag = urldefrag(u)
    return u

def url_host(u: str) -> str:
    return urlparse(u).netloc.lower()

def domain_of(u: str) -> str:
    ex = tldextract.extract(u)
    if not ex.suffix:
        return url_host(u)
    return f"{ex.domain}.{ex.suffix}".lower()

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()

def safe_fname(s: str, max_len: int = 140) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]+", "_", s)
    return s[:max_len].strip("_") or "file"

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def google_news_rss_urls(query: str) -> list[str]:
    # Public RSS, no API key
    from urllib.parse import quote_plus
    rss = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss)
    urls = []
    for e in feed.entries[:50]:
        if "link" in e:
            urls.append(norm_url(e.link))
    return urls

def extract_youtube_id(url: str) -> Optional[str]:
    u = urlparse(url)
    if "youtu.be" in u.netloc:
        vid = u.path.strip("/").split("/")[0]
        return vid or None
    if "youtube.com" in u.netloc:
        if u.path.startswith("/watch"):
            qs = dict([kv.split("=", 1) for kv in u.query.split("&") if "=" in kv])
            return qs.get("v")
        if u.path.startswith("/shorts/"):
            return u.path.split("/shorts/")[1].split("/")[0]
    return None

def get_pdf_text(pdf_path: Path) -> str:
    txt = ""
    try:
        reader = PdfReader(str(pdf_path))
        parts = []
        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                parts.append(t)
        txt = "\n\n".join(parts).strip()
    except Exception:
        txt = ""

    if len(txt.strip()) < 200:
        try:
            txt2 = pdfminer_extract_text(str(pdf_path)) or ""
            if len(txt2.strip()) > len(txt.strip()):
                txt = txt2.strip()
        except Exception:
            pass
    return txt.strip()

def trafilatura_extract(html: str, url: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
    downloaded = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        include_tables=True,
        include_images=False,
        output_format="json",
        with_metadata=True,
        favor_recall=True,
    )
    if not downloaded:
        return None, None, None
    try:
        j = json.loads(downloaded)
        text = (j.get("text") or "").strip() or None
        title = (j.get("title") or "").strip() or None
        date = (j.get("date") or "").strip() or None
        if date:
            try:
                date = dtparser.parse(date).isoformat()
            except Exception:
                pass
        return text, title, date
    except Exception:
        return None, None, None

def extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href:
            continue
        absu = urljoin(base_url, href)
        absu = norm_url(absu)
        if absu.startswith("http"):
            urls.append(absu)
    # de-dupe preserve order
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            out.append(u)
            seen.add(u)
    return out

def is_probably_article_url(u: str) -> bool:
    # crude heuristic
    p = urlparse(u).path.lower()
    if any(p.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".zip"]):
        return False
    if p.endswith(".pdf"):
        return True
    if p.count("/") >= 2 and any(tok in p for tok in ["202", "news", "article", "posts", "tag", "local", "press"]):
        return True
    return True

def reddit_search(keyword: str, limit: int = 25) -> list[dict]:
    # Public JSON. Respect rate limit.
    q = requests.utils.quote(keyword)
    url = f"https://www.reddit.com/search.json?q={q}&sort=new&limit={limit}"
    r = requests.get(url, headers={"User-Agent": UA}, timeout=25)
    if r.status_code != 200:
        return []
    data = r.json()
    children = data.get("data", {}).get("children", []) or []
    out = []
    for c in children:
        d = c.get("data", {}) or {}
        out.append({
            "title": d.get("title"),
            "permalink": "https://www.reddit.com" + (d.get("permalink") or ""),
            "subreddit": d.get("subreddit"),
            "created_utc": d.get("created_utc"),
            "selftext": d.get("selftext"),
            "url": d.get("url"),
            "score": d.get("score"),
            "num_comments": d.get("num_comments"),
        })
    return out

class Scraper:
    def __init__(self, out_dir: Path, delay_s: float, max_pages: int, max_depth: int, allow_domains: set[str]):
        self.out_dir = out_dir
        self.delay_s = delay_s
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.allow_domains = allow_domains

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": UA, "Accept": "*/*"})
        ensure_dir(self.out_dir)
        ensure_dir(self.out_dir / "raw" / "html")
        ensure_dir(self.out_dir / "raw" / "pdf")
        ensure_dir(self.out_dir / "raw" / "other")

        self.seen_urls: set[str] = set()
        self.seen_text_hashes: set[str] = set()
        self.count_by_domain: dict[str, int] = {}

        self.records_path = self.out_dir / "records.jsonl"

    def allowed(self, url: str) -> bool:
        d = domain_of(url)
        if not self.allow_domains:
            return True
        return d in self.allow_domains

    def bump_domain(self, url: str) -> bool:
        d = domain_of(url)
        n = self.count_by_domain.get(d, 0)
        if n >= self.max_pages:
            return False
        self.count_by_domain[d] = n + 1
        return True

    def save_record(self, rec: Record) -> None:
        with self.records_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")

    def fetch(self, url: str) -> tuple[int, str, bytes, str]:
        time.sleep(self.delay_s)
        r = self.session.get(url, timeout=35, allow_redirects=True)
        ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        final_url = norm_url(r.url)
        return r.status_code, final_url, r.content, ctype

    def handle_pdf(self, url: str, final_url: str, status: int, content: bytes) -> Record:
        fname = safe_fname(final_url.replace("://", "_"))
        pdf_path = self.out_dir / "raw" / "pdf" / f"{fname}.pdf"
        pdf_path.write_bytes(content)

        text = get_pdf_text(pdf_path)
        h = sha256(text) if text else None
        if h and h in self.seen_text_hashes:
            note = "dedup_text"
        else:
            note = None
            if h:
                self.seen_text_hashes.add(h)

        rec = Record(
            id=sha256(final_url)[:16],
            url=url,
            canonical_url=final_url,
            fetched_at=now_iso(),
            content_type="application/pdf",
            http_status=status,
            title=None,
            published_at=None,
            text=text if note != "dedup_text" else None,
            sha256_text=h,
            out_path=str(pdf_path.relative_to(self.out_dir)),
            notes=note,
            tags=["pdf"],
        )
        return rec

    def handle_youtube(self, url: str, final_url: str, status: int) -> Record:
        vid = extract_youtube_id(final_url) or extract_youtube_id(url)
        txt = None
        note = None
        if vid:
            try:
                parts = YouTubeTranscriptApi.get_transcript(vid)
                txt = "\n".join([p.get("text", "") for p in parts]).strip() or None
            except Exception as e:
                note = f"no_transcript:{type(e).__name__}"
        rec = Record(
            id=sha256(final_url)[:16],
            url=url,
            canonical_url=final_url,
            fetched_at=now_iso(),
            content_type="video/youtube",
            http_status=status,
            title=None,
            published_at=None,
            text=txt,
            sha256_text=sha256(txt) if txt else None,
            out_path=None,
            notes=note,
            tags=["youtube"],
        )
        return rec

    def handle_html(self, url: str, final_url: str, status: int, content: bytes) -> tuple[Record, list[str]]:
        html = content.decode("utf-8", errors="ignore")
        fname = safe_fname(final_url.replace("://", "_"))
        html_path = self.out_dir / "raw" / "html" / f"{fname}.html"
        html_path.write_text(html, encoding="utf-8", errors="ignore")

        text, title, published = trafilatura_extract(html, final_url)

        h = sha256(text) if text else None
        note = None
        if h:
            if h in self.seen_text_hashes:
                note = "dedup_text"
            else:
                self.seen_text_hashes.add(h)

        rec = Record(
            id=sha256(final_url)[:16],
            url=url,
            canonical_url=final_url,
            fetched_at=now_iso(),
            content_type="text/html",
            http_status=status,
            title=title,
            published_at=published,
            text=text if note != "dedup_text" else None,
            sha256_text=h,
            out_path=str(html_path.relative_to(self.out_dir)),
            notes=note,
            tags=["html"],
        )

        links = extract_links(html, final_url)
        links = [u for u in links if is_probably_article_url(u)]
        return rec, links

    def crawl(self, start_urls: Iterable[str]) -> None:
        q: list[tuple[str, int]] = []
        for u in start_urls:
            u = norm_url(u)
            if u.startswith("http"):
                q.append((u, 0))

        while q:
            url, depth = q.pop(0)
            if depth > self.max_depth:
                continue
            if url in self.seen_urls:
                continue
            self.seen_urls.add(url)
            if not self.allowed(url):
                continue
            if not self.bump_domain(url):
                continue

            host = url_host(url)
            try:
                status, final_url, body, ctype = self.fetch(url)
            except Exception as e:
                rec = Record(
                    id=sha256(url)[:16],
                    url=url,
                    canonical_url=url,
                    fetched_at=now_iso(),
                    content_type="error",
                    http_status=0,
                    notes=f"fetch_error:{type(e).__name__}",
                    tags=["error"],
                )
                self.save_record(rec)
                continue

            if "youtube.com" in host or "youtu.be" in host:
                rec = self.handle_youtube(url, final_url, status)
                self.save_record(rec)
                continue

            if ctype == "application/pdf" or final_url.lower().endswith(".pdf"):
                rec = self.handle_pdf(url, final_url, status, body)
                self.save_record(rec)
                continue

            if ctype.startswith("text/html") or ctype in ("", "text/plain"):
                rec, links = self.handle_html(url, final_url, status, body)
                self.save_record(rec)
                if status == 200:
                    for link in links:
                        if link not in self.seen_urls and self.allowed(link):
                            q.append((link, depth + 1))
                continue

            # other binaries
            fname = safe_fname(final_url.replace("://", "_"))
            outp = self.out_dir / "raw" / "other" / f"{fname}.bin"
            outp.write_bytes(body)
            rec = Record(
                id=sha256(final_url)[:16],
                url=url,
                canonical_url=final_url,
                fetched_at=now_iso(),
                content_type=ctype or "application/octet-stream",
                http_status=status,
                out_path=str(outp.relative_to(self.out_dir)),
                notes="downloaded_binary",
                tags=["binary"],
            )
            self.save_record(rec)

def init_out(out_dir: Path) -> None:
    ensure_dir(out_dir)
    (out_dir / "seeds.json").write_text(json.dumps({
        "seed_urls": SEED_URLS,
        "google_news_rss_queries": GOOGLE_NEWS_RSS_QUERIES,
        "reddit_keywords": REDDIT_KEYWORDS,
    }, indent=2), encoding="utf-8")
    print(f"wrote {out_dir/'seeds.json'}")

def load_seeds(path: Path) -> tuple[list[str], list[str], list[str]]:
    j = json.loads(path.read_text(encoding="utf-8"))
    return j.get("seed_urls", []), j.get("google_news_rss_queries", []), j.get("reddit_keywords", [])

def build_allow_domains(allow_domains_arg: list[str], seed_urls: list[str]) -> set[str]:
    allow = set([d.strip().lower() for d in allow_domains_arg if d.strip()])
    # auto-allow seed domains if allow list is empty
    if not allow:
        for u in seed_urls:
            allow.add(domain_of(u))
    return allow

def harvest_rss(queries: list[str]) -> list[str]:
    urls = []
    for q in queries:
        try:
            urls.extend(google_news_rss_urls(q))
        except Exception:
            continue
        time.sleep(0.8)
    # dedup
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            out.append(u)
            seen.add(u)
    return out

def dump_reddit(out_dir: Path, keywords: list[str]) -> list[str]:
    # store reddit results as records too
    out = []
    path = out_dir / "reddit.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for kw in keywords:
            time.sleep(1.1)
            items = reddit_search(kw, limit=25)
            for it in items:
                f.write(json.dumps({"keyword": kw, "item": it}, ensure_ascii=False) + "\n")
                # enqueue permalink and linked url
                if it.get("permalink"):
                    out.append(norm_url(it["permalink"]))
                if it.get("url") and str(it["url"]).startswith("http"):
                    out.append(norm_url(it["url"]))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dc_corpus", help="output dir")
    ap.add_argument("--init", action="store_true", help="write seeds.json then exit")
    ap.add_argument("--seeds", default="seeds.json", help="path to seeds.json")
    ap.add_argument("--delay", type=float, default=DEFAULT_DELAY_S)
    ap.add_argument("--max-pages", type=int, default=120, help="per-domain cap")
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--allow-domain", action="append", default=[], help="repeatable, e.g. --allow-domain sourcenm.com")
    ap.add_argument("--no-rss", action="store_true")
    ap.add_argument("--no-reddit", action="store_true")
    args = ap.parse_args()

    out_dir = Path(args.out).resolve()
    ensure_dir(out_dir)

    if args.init:
        init_out(out_dir)
        return

    seeds_path = Path(args.seeds)
    if not seeds_path.exists():
        # fallback to out/seeds.json
        alt = out_dir / "seeds.json"
        if alt.exists():
            seeds_path = alt
        else:
            print("missing seeds.json; run: python border_dc_scraper.py --init --out dc_corpus", file=sys.stderr)
            sys.exit(2)

    seed_urls, rss_queries, reddit_keywords = load_seeds(seeds_path)
    allow_domains = build_allow_domains(args.allow_domain, seed_urls)

    harvested = []
    if not args.no_rss and rss_queries:
        harvested = harvest_rss(rss_queries)

    reddit_urls = []
    if not args.no_reddit and reddit_keywords:
        reddit_urls = dump_reddit(out_dir, reddit_keywords)

    start_urls = []
    start_urls.extend(seed_urls)
    start_urls.extend(harvested)
    start_urls.extend(reddit_urls)

    # final dedup
    start_urls = [u for u in start_urls if u.startswith("http")]
    seen = set()
    final = []
    for u in start_urls:
        u = norm_url(u)
        if u not in seen:
            final.append(u)
            seen.add(u)

    (out_dir / "start_urls.txt").write_text("\n".join(final), encoding="utf-8")

    s = Scraper(
        out_dir=out_dir,
        delay_s=args.delay,
        max_pages=args.max_pages,
        max_depth=args.depth,
        allow_domains=allow_domains,
    )
    s.crawl(final)
    print(f"done. records: {out_dir/'records.jsonl'}")

if __name__ == "__main__":
    main()
