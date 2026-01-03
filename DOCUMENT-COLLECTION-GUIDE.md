# 📚 Document Collection Guide

**Objective:** Populate `docs/` directory with source materials for Civic Ledger API

---

## 🎯 Directory Structure

```
docs/
├── legal/                    # Texas/NM statutes
├── precedents/              # Other cities' agreements  
├── board-minutes/           # EPWater/Council minutes
├── cost-studies/            # Utility cost analyses
├── development-agreements/  # El Paso DC agreements
└── technical-specs/         # AMI, infrastructure
```

---

## 🔥 HIGH PRIORITY - Get These First

### 1. Texas Legal Authorities

**Texas Water Code Chapter 13**
- Source: https://statutes.capitol.texas.gov/
- Navigate to: Water Code → Chapter 13 (Water and Sewer Utility Rate Regulation)
- Download as PDF
- Save to: `docs/legal/texas-water-code-chapter-13.pdf`

**Texas Local Government Code Chapter 380**
- Source: https://statutes.capitol.texas.gov/
- Navigate to: Local Government Code → Chapter 380 (Economic Development)
- Save to: `docs/legal/texas-local-govt-code-380.pdf`

**Why critical:** These are the foundational authorities for:
- Citation validation
- Legal authority searches
- Policy generation

---

### 2. EPWater Board Minutes (2023-2024)

**How to get:**
```bash
# Public records request template:
To: EPWater Public Information Officer
Subject: Public Information Act Request - Board Minutes

I am requesting electronic copies of all El Paso Water 
Board of Directors meeting minutes from January 1, 2023 
through December 31, 2024.

Format preference: PDF
Delivery: Email or download link

Thank you,
[Your name]
```

**What to look for in minutes:**
- Data center mentions
- Large customer discussions
- Rate structure changes
- Cost-of-service studies

**Save to:** `docs/board-minutes/epwater-YYYY-MM.pdf`

---

### 3. Border Data Center Development Agreement

**If publicly available:**
- Check El Paso City Clerk records
- Search: "development agreement" + "data center"
- Look for Santa Teresa / Border area

**Save to:** `docs/development-agreements/border-dc-agreement.pdf`

---

## 📊 MEDIUM PRIORITY - Precedent Examples

### Loudoun County, VA

**Known for:** Extensive data center development agreements

**Where to find:**
- Loudoun County Department of Economic Development
- https://www.loudoun.gov/
- Search public records for "data center development agreement"

**Look for:**
- Infrastructure escrow requirements
- Water/utility allocation
- Performance bonds

**Save to:** `docs/precedents/loudoun-county/`

---

### Mesa, AZ

**Known for:** Large industrial water contracts

**Where to find:**
- City of Mesa Water Resources
- https://www.mesaaz.gov/
- Public records request

**Save to:** `docs/precedents/mesa/`

---

## 🛠 TOOLS TO HELP

### Process Existing dc_corpus

```bash
chmod +x organize-docs.sh process-corpus.sh

# See organization recommendations
./organize-docs.sh

# Analyze what's in dc_corpus
./process-corpus.sh
```

### Convert HTML to PDF

If you have HTML files in dc_corpus:

```bash
# Using wkhtmltopdf
wkhtmltopdf input.html output.pdf

# Or using Chrome headless
chrome --headless --print-to-pdf=output.pdf input.html
```

### Extract Text from PDFs

```python
# Simple extraction script
import PyPDF2

def extract_text(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# Usage
text = extract_text('docs/legal/texas-water-code.pdf')
print(text)
```

---

## 📋 Document Checklist

### Legal Authorities
- [ ] Texas Water Code Chapter 13
- [ ] Texas Local Government Code Chapter 380
- [ ] New Mexico Public Utilities Act
- [ ] El Paso City Charter (utility provisions)

### Board Minutes
- [ ] EPWater Board 2024 (all months)
- [ ] EPWater Board 2023 (all months)
- [ ] El Paso City Council 2024 (data center mentions)

### Development Agreements
- [ ] Border/Santa Teresa data center agreement
- [ ] Any other El Paso DC agreements

### Precedents
- [ ] Loudoun County development agreements (3-5 examples)
- [ ] Mesa water contracts (2-3 examples)
- [ ] Other cities' data center agreements

### Cost Studies
- [ ] EPWater cost-of-service study (latest)
- [ ] Rate impact analyses

---

## 🔍 Finding Public Records

### El Paso Resources

**City of El Paso:**
- City Clerk: https://www.elpasotexas.gov/city-clerk
- Public records: cityclerk@elpasotexas.gov

**EPWater:**
- Public Information: https://www.epwater.org/
- Records requests: pio@epwater.org

### Texas Public Information Act (PIA)

**Template request:**
```
Under the Texas Public Information Act (Gov't Code Chapter 552),
I am requesting copies of:

[Specific description of records]

Date range: [Start] to [End]
Format: Electronic (PDF preferred)

If any portion is deemed exempt, please provide all non-exempt portions.

Thank you,
[Your name]
[Contact info]
```

**Response time:** 10 business days

---

## 📈 Progress Tracking

Track what you've collected:

```bash
# Count documents in each category
find docs/legal -name "*.pdf" | wc -l
find docs/board-minutes -name "*.pdf" | wc -l
find docs/precedents -name "*.pdf" | wc -l

# Total document count
find docs -name "*.pdf" -o -name "*.md" | wc -l
```

---

## 🚀 After Collection

Once you have documents:

1. **Update document_loader.py** to index new files
2. **Test citation validation** on real documents
3. **Verify search** works across all categories
4. **Redeploy** to Fly.io with new documents

```bash
# Quick test
./quick-test.sh

# Full deployment
flyctl deploy --app civic-ledger-elpaso
```

---

## 💡 Pro Tips

1. **Start with legal authorities** - Most critical for citations
2. **Board minutes are gold** - Show actual decision-making
3. **Precedents prove feasibility** - "Other cities did this"
4. **Keep originals** - Never delete source PDFs
5. **Document sources** - Track where each file came from

---

## 📞 Need Help?

- **Can't find a document?** Try a PIA request
- **Format issues?** Use conversion tools above
- **Legal questions?** Documents are for reference only

---

**Start with:** Texas Water Code Chapter 13 (30 min to download)
**Next:** EPWater board minutes PIA request (submit today)
**Then:** Process existing dc_corpus materials

**Let's build that document library! 📚**
