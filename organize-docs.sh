#!/bin/bash

echo "📚 Civic Ledger - Source Material Organization"
echo "=============================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="/Users/chriscelaya/Downloads/civic-ledger-elpaso"

# Create organized directory structure
echo -e "\n${YELLOW}Step 1: Creating organized directory structure...${NC}"

mkdir -p "$PROJECT_ROOT/docs/legal" 2>/dev/null
mkdir -p "$PROJECT_ROOT/docs/precedents" 2>/dev/null
mkdir -p "$PROJECT_ROOT/docs/board-minutes" 2>/dev/null
mkdir -p "$PROJECT_ROOT/docs/cost-studies" 2>/dev/null
mkdir -p "$PROJECT_ROOT/docs/development-agreements" 2>/dev/null
mkdir -p "$PROJECT_ROOT/docs/technical-specs" 2>/dev/null

echo -e "${GREEN}✓ Directory structure created${NC}"

# Show current structure
echo -e "\n${YELLOW}Step 2: Current docs/ structure:${NC}"
tree "$PROJECT_ROOT/docs" -L 2 2>/dev/null || ls -R "$PROJECT_ROOT/docs"

# Count files in dc_corpus
echo -e "\n${YELLOW}Step 3: Analyzing dc_corpus...${NC}"

if [ -d "$PROJECT_ROOT/dc_corpus" ]; then
    pdf_count=$(find "$PROJECT_ROOT/dc_corpus" -name "*.pdf" 2>/dev/null | wc -l)
    html_count=$(find "$PROJECT_ROOT/dc_corpus" -name "*.html" 2>/dev/null | wc -l)
    json_count=$(find "$PROJECT_ROOT/dc_corpus" -name "*.json*" 2>/dev/null | wc -l)
    
    echo "Found in dc_corpus:"
    echo "  PDFs: $pdf_count"
    echo "  HTML: $html_count"
    echo "  JSON: $json_count"
else
    echo -e "${YELLOW}⚠️  dc_corpus directory not found${NC}"
fi

# Recommended organization
echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Recommended Document Organization${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

cat << 'EOF'

docs/
├── legal/                           # TX/NM statutes & regulations
│   ├── texas-water-code.pdf
│   ├── texas-local-govt-code.pdf
│   ├── nm-public-utilities-act.pdf
│   └── legal-authorities.md         # ← Already exists
│
├── precedents/                      # Other cities' agreements
│   ├── loudoun-county/
│   │   ├── data-center-dev-agreement.pdf
│   │   └── infrastructure-escrow.pdf
│   ├── mesa-az/
│   │   └── water-contract.pdf
│   └── comparable-jurisdictions.md  # ← Already exists
│
├── board-minutes/                   # EPWater/City Council minutes
│   ├── epwater-2024-01.pdf
│   ├── epwater-2024-02.pdf
│   └── city-council-2024-Q1.pdf
│
├── cost-studies/                    # Utility cost analyses
│   ├── epwater-cost-of-service-2023.pdf
│   └── rate-impact-analysis.pdf
│
├── development-agreements/          # Actual El Paso agreements
│   ├── border-dc-development-agreement.pdf
│   └── santa-teresa-dc-agreement.pdf
│
└── technical-specs/                 # AMI, infrastructure specs
    └── epwater-ami-architecture.md  # ← Already exists

EOF

echo -e "\n${YELLOW}Step 4: Document Collection Checklist${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

cat << 'EOF'

Priority Documents to Collect:

HIGH PRIORITY (for citation validation):
□ Texas Water Code Chapter 13 (utility rates)
□ Texas Local Government Code Chapter 380 (economic development)
□ EPWater Board Minutes (2023-2024)
□ City of El Paso development agreements with data centers

MEDIUM PRIORITY (for precedents):
□ Loudoun County data center development agreements
□ Mesa, AZ water contracts for large users
□ Raleigh-Durham infrastructure escrow requirements

LOW PRIORITY (nice to have):
□ EPWater cost-of-service studies
□ Rate impact analyses
□ Technical specifications from other utilities

EOF

echo -e "\n${YELLOW}Step 5: Next Actions${NC}"

cat << 'EOF'

To populate your docs/ directory:

1. LEGAL AUTHORITIES:
   - Download Texas Water Code Chapter 13
   - Download relevant Local Government Code sections
   - Save as PDFs in docs/legal/

2. BOARD MINUTES:
   - Request from EPWater: board minutes 2023-2024
   - Look for keywords: "data center", "large customer", "rate"
   - Save in docs/board-minutes/

3. PRECEDENT AGREEMENTS:
   - Research Loudoun County public records
   - Find Mesa, AZ water department agreements
   - Save in docs/precedents/[jurisdiction]/

4. PROCESS dc_corpus MATERIALS:
   Run: ./organize-corpus.sh
   This will sort existing materials into proper folders

EOF

echo -e "\n${GREEN}✓ Organization guide complete!${NC}"
echo -e "\nReady to collect documents? Run individual scripts below."
