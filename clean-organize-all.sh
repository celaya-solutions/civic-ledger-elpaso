#!/bin/bash

echo "🧹 Clean & Organize Civic Ledger Project"
echo "========================================"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="/Users/chriscelaya/Downloads/civic-ledger-elpaso"
cd "$PROJECT_ROOT"

echo -e "\n${YELLOW}Step 1: Archive old/duplicate files${NC}"

# Create archive directory
mkdir -p archive/{old-scripts,duplicate-prompts,test-files,scraped-raw}

# Archive duplicate system prompts (keep optimal only)
echo "Archiving duplicate system prompts..."
mv docs/system-prompt.md archive/duplicate-prompts/ 2>/dev/null
mv docs/system-prompt-gpt.md archive/duplicate-prompts/ 2>/dev/null

# Archive old test scripts
echo "Archiving old scripts..."
mv battle-test.sh archive/old-scripts/ 2>/dev/null
mv battle-test-complete.sh archive/old-scripts/ 2>/dev/null
mv discover-endpoints.sh archive/old-scripts/ 2>/dev/null

# Archive conversation starters (not needed in production docs/)
mv docs/conversation-starters-library.md archive/old-scripts/ 2>/dev/null

# Archive .DS_Store files
find . -name ".DS_Store" -delete

echo -e "${GREEN}✓ Archived old files${NC}"

echo -e "\n${YELLOW}Step 2: Organize docs/ directory${NC}"

# Create clean structure
mkdir -p docs/{legal,board-minutes,development-agreements,cost-studies,precedents,technical,config}

# Move existing files to proper locations
echo "Organizing docs..."
mv docs/legal-authorities.md docs/legal/ 2>/dev/null
mv docs/texas-water-code-chatper-13.pdf docs/legal/ 2>/dev/null
mv docs/epwater-ami-architecture.md docs/technical/ 2>/dev/null
mv docs/comparable-jurisdictions.md docs/precedents/ 2>/dev/null
mv docs/system-prompt-optimal.md docs/config/ 2>/dev/null

echo -e "${GREEN}✓ Organized docs/${NC}"

echo -e "\n${YELLOW}Step 3: Organize project root${NC}"

# Create clean directory structure
mkdir -p scripts/{deployment,testing,extraction}
mkdir -p documentation

# Move deployment scripts
mv deploy-production.sh scripts/deployment/ 2>/dev/null
mv quick-fix-deploy.sh scripts/deployment/ 2>/dev/null

# Move testing scripts
mv test-citations-rigorous.sh scripts/testing/ 2>/dev/null
mv audit-docs-quality.sh scripts/testing/ 2>/dev/null
mv quick-test.sh scripts/testing/ 2>/dev/null
mv battle-test-all-9.sh scripts/testing/ 2>/dev/null

# Move extraction scripts
mv extract-and-categorize.py scripts/extraction/ 2>/dev/null
mv border_dc_scraper.py scripts/extraction/ 2>/dev/null
mv process-corpus.sh scripts/extraction/ 2>/dev/null

# Move documentation
mv SHIP-IT-PRODUCTION.md documentation/ 2>/dev/null
mv CUSTOMGPT-SETUP.md documentation/ 2>/dev/null
mv DEPLOYMENT-SUMMARY.md documentation/ 2>/dev/null
mv DEPLOYMENT.md documentation/ 2>/dev/null
mv CHECKLIST.md documentation/ 2>/dev/null
mv DOCUMENT-COLLECTION-GUIDE.md documentation/ 2>/dev/null
mv STATUS-NOW.md documentation/ 2>/dev/null
mv SYSTEM-PROMPT-GUIDE.md documentation/ 2>/dev/null
mv INPUT-VALIDATION-FIX.md documentation/ 2>/dev/null
mv CITATION-TESTING-GUIDE.md documentation/ 2>/dev/null

# Move remaining organization scripts
mv organize-docs.sh scripts/extraction/ 2>/dev/null

echo -e "${GREEN}✓ Organized project structure${NC}"

echo -e "\n${YELLOW}Step 4: Create clean file structure${NC}"

cat > PROJECT-STRUCTURE.md << 'EOF'
# Civic Ledger Project Structure

```
civic-ledger-elpaso/
├── README.md                          # Main project overview
├── PROJECT-STRUCTURE.md               # This file
│
├── Server Components
│   ├── server.py                      # FastAPI server (production)
│   ├── citation_validator.py          # Citation validation
│   ├── document_loader.py             # Document loading
│   ├── template_generator.py          # Template generation
│   ├── feasibility_checker.py         # Feasibility checks
│   ├── Dockerfile                     # Container build
│   ├── fly.toml                       # Fly.io config
│   ├── openapi.yaml                   # API specification
│   └── requirements.txt               # Python dependencies
│
├── docs/                              # Source documents for API
│   ├── config/
│   │   └── system-prompt-optimal.md   # CustomGPT instructions
│   ├── legal/
│   │   ├── legal-authorities.md       # TX/NM statutes
│   │   └── texas-water-code-chatper-13.pdf
│   ├── precedents/
│   │   └── comparable-jurisdictions.md
│   ├── technical/
│   │   └── epwater-ami-architecture.md
│   ├── board-minutes/
│   ├── development-agreements/
│   └── cost-studies/
│
├── scripts/
│   ├── deployment/                    # Deployment tools
│   │   ├── deploy-production.sh
│   │   └── quick-fix-deploy.sh
│   ├── testing/                       # Testing tools
│   │   ├── test-citations-rigorous.sh
│   │   ├── audit-docs-quality.sh
│   │   ├── quick-test.sh
│   │   └── battle-test-all-9.sh
│   └── extraction/                    # Data processing
│       ├── extract-and-categorize.py
│       ├── border_dc_scraper.py
│       ├── process-corpus.sh
│       └── organize-docs.sh
│
├── documentation/                     # Project guides
│   ├── SHIP-IT-PRODUCTION.md
│   ├── CUSTOMGPT-SETUP.md
│   ├── DEPLOYMENT.md
│   ├── DOCUMENT-COLLECTION-GUIDE.md
│   ├── CITATION-TESTING-GUIDE.md
│   └── STATUS-NOW.md
│
├── dc_corpus/                         # Raw scraped data
│   ├── raw/
│   │   ├── html/
│   │   ├── pdf/
│   │   └── other/
│   ├── records.jsonl
│   ├── reddit.jsonl
│   └── minimal.jsonl
│
├── archive/                           # Old/duplicate files
│   ├── old-scripts/
│   ├── duplicate-prompts/
│   ├── test-files/
│   └── scraped-raw/
│
└── civic-server/                      # Python venv (local only)
```

## Quick Commands

**Deploy:**
```bash
./scripts/deployment/deploy-production.sh
```

**Test:**
```bash
./scripts/testing/test-citations-rigorous.sh
```

**Extract corpus:**
```bash
python scripts/extraction/extract-and-categorize.py
```

**View docs:**
- API: https://civic-ledger-elpaso.fly.dev/docs
- Local: open documentation/
EOF

echo -e "${GREEN}✓ Created PROJECT-STRUCTURE.md${NC}"

echo -e "\n${YELLOW}Step 5: Update README with timestamp${NC}"

TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S %Z")

cat > README.md << EOF
# Civic Ledger — El Paso Proof Engine

**Production-ready civic accountability framework for El Paso, TX**

Built by [Celaya Solutions](https://celayasolutions.com)

**Last Updated:** $TIMESTAMP

---

## 🚀 Quick Start

### Deploy Server
\`\`\`bash
./scripts/deployment/deploy-production.sh
\`\`\`

### Configure CustomGPT
1. Import actions: \`https://civic-ledger-elpaso.fly.dev/openapi.json\`
2. Use instructions: \`docs/config/system-prompt-optimal.md\`
3. See full guide: \`documentation/CUSTOMGPT-SETUP.md\`

### Test Citations
\`\`\`bash
./scripts/testing/test-citations-rigorous.sh
\`\`\`

---

## 📊 Project Status

**Deployment:**
- ✅ FastAPI server live at civic-ledger-elpaso.fly.dev
- ✅ 9 production endpoints operational
- ✅ CORS enabled for CustomGPT integration

**Documents:**
- ✅ Texas Water Code Chapter 13 (PDF)
- ✅ Legal authorities markdown
- ✅ EPWater AMI architecture
- ✅ Comparable jurisdictions

**CustomGPT:**
- ✅ OpenAPI spec available
- ✅ System prompt optimized
- ⏳ Configuration in progress

---

## 📁 Project Structure

See [PROJECT-STRUCTURE.md](PROJECT-STRUCTURE.md) for complete file organization.

**Key directories:**
- \`server.py\` - Main API server
- \`docs/\` - Source documents for citations
- \`scripts/\` - Deployment, testing, extraction tools
- \`documentation/\` - Setup guides and references

---

## 🛠 Development

### Local Testing
\`\`\`bash
# Activate venv
source civic-server/bin/activate

# Run locally
uvicorn server:app --reload

# Test endpoints
./scripts/testing/quick-test.sh
\`\`\`

### Extract Corpus Data
\`\`\`bash
python scripts/extraction/extract-and-categorize.py
\`\`\`

### Deploy to Fly.io
\`\`\`bash
flyctl deploy --app civic-ledger-elpaso
\`\`\`

---

## 📖 Documentation

- **[CUSTOMGPT-SETUP.md](documentation/CUSTOMGPT-SETUP.md)** - Configure CustomGPT
- **[DEPLOYMENT.md](documentation/DEPLOYMENT.md)** - Deployment guide
- **[CITATION-TESTING-GUIDE.md](documentation/CITATION-TESTING-GUIDE.md)** - Test citations
- **[DOCUMENT-COLLECTION-GUIDE.md](documentation/DOCUMENT-COLLECTION-GUIDE.md)** - Collect source docs

---

## 🎯 Mission

Generate verifiable civic control frameworks that protect El Paso residents from ratepayer cross-subsidy related to data center utility impacts.

**Principles:**
- Pro-growth AND pro-fairness
- Evidence-based (80% documented, 20% inference, 0% speculation)
- No personal attacks — design systems, not accusations
- All outputs implementable by existing staff

---

## 🔗 Links

- **API Docs:** https://civic-ledger-elpaso.fly.dev/docs
- **OpenAPI Spec:** https://civic-ledger-elpaso.fly.dev/openapi.json
- **Health Check:** https://civic-ledger-elpaso.fly.dev/health

---

## 📝 License

Built for public benefit. Use responsibly.

**Legal Disclaimer:** This tool provides technical framework templates only — NOT legal advice. All ordinances, resolutions, and contracts require review by qualified legal counsel before introduction, adoption, or execution.

---

**Last Updated:** $TIMESTAMP
EOF

echo -e "${GREEN}✓ Updated README.md${NC}"

echo -e "\n${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}Organization Complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

echo -e "\n${GREEN}Project structure:${NC}"
echo "  ✅ Server files in root"
echo "  ✅ docs/ organized by category"
echo "  ✅ scripts/ organized by function"
echo "  ✅ documentation/ centralized"
echo "  ✅ archive/ for old files"
echo "  ✅ README.md updated with timestamp"
echo "  ✅ PROJECT-STRUCTURE.md created"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Review: cat PROJECT-STRUCTURE.md"
echo "2. Review: cat README.md"
echo "3. Commit: git add . && git commit -m 'Clean project structure'"
echo "4. Deploy: ./scripts/deployment/deploy-production.sh"

echo -e "\n${GREEN}✓ Done!${NC}"
