#!/usr/bin/env python3
"""
Extract & Categorize dc_corpus → docs/
Handles PDFs, HTML, skips corrupted files
Auto-categorizes by content keywords
"""

from pathlib import Path
from pypdf import PdfReader
import trafilatura
from tqdm import tqdm
import re

# Directories
CORPUS = Path("dc_corpus")
DOCS = Path("docs")

# Category mappings (keyword → directory)
CATEGORIES = {
    "legal": ["statute", "code", "regulation", "law", "ordinance", "charter"],
    "board-minutes": ["board", "minutes", "meeting", "council", "commission"],
    "development-agreements": ["development agreement", "memorandum", "contract"],
    "cost-studies": ["cost", "rate", "study", "analysis", "fiscal"],
    "precedents": ["loudoun", "mesa", "raleigh", "precedent"],
    "technical": ["ami", "meter", "infrastructure", "technical", "specification"],
}

def extract_pdf(pdf_path: Path) -> str:
    """Extract text from PDF, skip if corrupted"""
    try:
        reader = PdfReader(pdf_path)
        text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
        return text.strip()
    except Exception as e:
        print(f"⚠️  Skipping corrupted PDF: {pdf_path.name} ({e})")
        return None

def extract_html(html_path: Path) -> str:
    """Extract text from HTML using trafilatura"""
    try:
        html = html_path.read_text(encoding="utf-8", errors="ignore")
        text = trafilatura.extract(html, include_comments=False, include_tables=True)
        return text or ""
    except Exception as e:
        print(f"⚠️  Skipping HTML: {html_path.name} ({e})")
        return None

def categorize(text: str, filename: str) -> str:
    """Auto-categorize based on content keywords"""
    text_lower = (text + " " + filename).lower()
    
    # Score each category
    scores = {}
    for category, keywords in CATEGORIES.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        scores[category] = score
    
    # Return highest scoring category, default to "other"
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "other"

def clean_filename(name: str) -> str:
    """Clean up ugly scraper filenames"""
    # Remove URL encoding
    name = name.replace("https_", "").replace("http_", "")
    name = re.sub(r"_[a-f0-9]{32,}", "", name)  # Remove hash IDs
    name = re.sub(r"\.pdf\.pdf$", ".pdf", name)  # Fix double extensions
    name = re.sub(r"[^a-zA-Z0-9\-_.]", "_", name)  # Remove special chars
    name = re.sub(r"_+", "_", name)  # Collapse multiple underscores
    return name[:100]  # Limit length

def main():
    print("🔄 Extract & Categorize dc_corpus → docs/")
    print("=" * 50)
    
    # Find all files
    pdfs = list(CORPUS.rglob("*.pdf"))
    htmls = list(CORPUS.rglob("*.html"))
    total = len(pdfs) + len(htmls)
    
    print(f"Found: {len(pdfs)} PDFs, {len(htmls)} HTML files")
    print()
    
    stats = {"success": 0, "skipped": 0, "categories": {}}
    
    # Process PDFs
    for pdf in tqdm(pdfs, desc="PDFs", unit="file"):
        text = extract_pdf(pdf)
        if not text:
            stats["skipped"] += 1
            continue
        
        # Categorize
        category = categorize(text, pdf.name)
        
        # Create category dir
        cat_dir = DOCS / category
        cat_dir.mkdir(exist_ok=True)
        
        # Write markdown
        clean_name = clean_filename(pdf.stem) + ".md"
        out_path = cat_dir / clean_name
        
        content = f"# {pdf.stem}\n\n**Source:** {pdf}\n\n---\n\n{text}"
        out_path.write_text(content, encoding="utf-8")
        
        stats["success"] += 1
        stats["categories"][category] = stats["categories"].get(category, 0) + 1
    
    # Process HTML
    for html in tqdm(htmls, desc="HTML", unit="file"):
        text = extract_html(html)
        if not text or len(text) < 100:  # Skip empty/tiny files
            stats["skipped"] += 1
            continue
        
        # Categorize
        category = categorize(text, html.name)
        
        # Create category dir
        cat_dir = DOCS / category
        cat_dir.mkdir(exist_ok=True)
        
        # Write markdown
        clean_name = clean_filename(html.stem) + ".md"
        out_path = cat_dir / clean_name
        
        content = f"# {html.stem}\n\n**Source:** {html}\n\n---\n\n{text}"
        out_path.write_text(content, encoding="utf-8")
        
        stats["success"] += 1
        stats["categories"][category] = stats["categories"].get(category, 0) + 1
    
    # Summary
    print()
    print("=" * 50)
    print("✅ COMPLETE")
    print(f"Processed: {stats['success']}/{total}")
    print(f"Skipped: {stats['skipped']}")
    print()
    print("Categories:")
    for cat, count in sorted(stats["categories"].items()):
        print(f"  {cat}: {count} files")
    print()
    print(f"Output: {DOCS}/")

if __name__ == "__main__":
    main()
