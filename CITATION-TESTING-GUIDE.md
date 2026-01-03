# 🧪 Citation Testing & Data Quality Guide

## Problem

You need to verify:
1. **Citation accuracy** - Is the LLM finding real text in docs?
2. **Data quality** - Is there irrelevant scraped data polluting citations?

---

## ✅ SOLUTION 1: Rigorous Citation Testing

**Test the citation validation endpoint with known good/bad examples:**

```bash
chmod +x test-citations-rigorous.sh
./test-citations-rigorous.sh
```

**What it tests:**
- ✅ Exact matches (should find)
- ✅ Partial matches (should find)
- ❌ Nonsense text (should NOT find)
- ❌ Wrong document (should NOT find)
- ❌ Similar but incorrect (should NOT find)
- 🔍 Edge cases (case sensitivity, short queries)

**Expected output:**
```
Test Results Summary
═══════════════════
Total Tests: 8
Passed: 8
Failed: 0
🎉 All citation tests passed!
```

---

## ✅ SOLUTION 2: Audit Document Quality

**Check for irrelevant scraped content:**

```bash
chmod +x audit-docs-quality.sh
./audit-docs-quality.sh
```

**What it checks:**
- Relevant keyword density (water, utility, rate, etc.)
- Junk indicators (reddit, twitter, ads, cookies)
- File sizes and content types
- Produces review list of suspicious files

**Output:** List of files that may need removal

---

## 🎯 RECOMMENDED WORKFLOW

### 1. Test Current Citations (5 min)
```bash
./test-citations-rigorous.sh
```

**If tests FAIL:**
- Check `citation_validator.py` implementation
- Verify docs/ files are readable
- Check for encoding issues

**If tests PASS:**
- Citations are working correctly
- Problem is likely data quality, not validator

---

### 2. Audit Document Quality (10 min)
```bash
./audit-docs-quality.sh
```

**Review output for:**
- Files with high "junk indicators"
- Files with low "relevant mentions"
- Scraped social media content
- Duplicate information

---

### 3. Manual Document Review (30 min)

**For EACH file in docs/:**

```bash
# Quick preview
head -50 docs/filename.md

# Search for quality
grep -i "water\|utility\|data center" docs/filename.md | wc -l
grep -i "reddit\|twitter\|upvote" docs/filename.md | wc -l
```

**Keep if:**
- ✅ Official source (statute, regulation, board minutes)
- ✅ Precedent example (other cities' agreements)
- ✅ Technical specification (AMI architecture)
- ✅ Analysis/summary you created

**Remove if:**
- ❌ Social media scrape (Reddit, Twitter)
- ❌ News article comments
- ❌ Advertisement content
- ❌ Generic web page scraped data
- ❌ Cookie policies, terms of service
- ❌ Duplicate of another file

---

### 4. Clean Up docs/ (15 min)

**Move junk to archive:**

```bash
# Create archive
mkdir -p docs-archive/scraped-junk

# Move irrelevant files
mv docs/reddit-thread-xyz.md docs-archive/scraped-junk/
mv docs/news-comments.md docs-archive/scraped-junk/

# Keep only high-quality sources
```

**Final docs/ should contain ONLY:**
```
docs/
├── legal-authorities.md           ✅ TX/NM statutes
├── epwater-ami-architecture.md    ✅ Technical specs
├── comparable-jurisdictions.md    ✅ Precedent examples
├── system-prompt-optimal.md       ✅ CustomGPT config
└── [New PDFs you collect]
```

---

## 🔬 ADVANCED: Test with CustomGPT

Once docs/ is clean, test citation accuracy through CustomGPT:

### Test 1: Known Good Citation
**Prompt:**
```
Validate that "Texas Water Code Chapter 13" appears in legal-authorities.md
```

**Expected:**
- Uses validate_citation action
- Returns GREEN confidence
- Shows exact match

### Test 2: Known Bad Citation
**Prompt:**
```
Validate that "California Penal Code" appears in legal-authorities.md
```

**Expected:**
- Uses validate_citation action
- Returns RED or "No matches found"
- Does NOT hallucinate a match

### Test 3: Policy Generation with Citations
**Prompt:**
```
Generate a staff checklist for implementing a data center water ledger. 
Validate all legal authority citations.
```

**Expected:**
- Uses validate_citation for each claim
- Only includes GREEN citations
- Flags YELLOW inferences
- No false citations

---

## 📊 QUALITY METRICS

**Good document collection:**
- 80%+ official sources (statutes, board minutes, agreements)
- 20% analysis/summaries you created
- 0% social media scrapes
- 0% advertisement content

**Citation accuracy:**
- 95%+ precision (found citations are real)
- 90%+ recall (real citations are found)
- 0% false positives (hallucinated citations)

---

## 🚨 RED FLAGS

**If you see these in citations, data is bad:**

```
Source: [Reddit comment thread]
Source: [Twitter discussion]
Source: [News article comments section]
Source: [Advertisement copy]
Source: [Cookie policy]
```

**These indicate scraped junk, not authoritative sources.**

---

## ✅ NEXT STEPS

1. **Run tests** (10 min)
   ```bash
   ./test-citations-rigorous.sh
   ./audit-docs-quality.sh
   ```

2. **Review flagged files** (20 min)
   - Check /tmp/docs-to-review.txt
   - Manually review each file
   - Move junk to docs-archive/

3. **Re-test** (5 min)
   ```bash
   ./test-citations-rigorous.sh
   ```

4. **Deploy clean docs** (5 min)
   ```bash
   flyctl deploy --app civic-ledger-elpaso
   ```

5. **Test with CustomGPT** (10 min)
   - Try citation validation prompts
   - Verify no false positives
   - Check policy generation quality

---

**Start with:** `./test-citations-rigorous.sh` to baseline current accuracy! 🧪
