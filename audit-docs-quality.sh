#!/bin/bash

echo "🧹 Clean Irrelevant Data from docs/"
echo "===================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DOCS_DIR="/Users/chriscelaya/Downloads/civic-ledger-elpaso/docs"

echo -e "\n${YELLOW}Step 1: Audit current docs/${NC}"

# List all files with sizes
echo -e "\n${BLUE}Current files:${NC}"
find "$DOCS_DIR" -type f -exec ls -lh {} \; | awk '{print $9, "("$5")"}'

echo -e "\n${YELLOW}Step 2: Check for irrelevant content${NC}"

# Function to scan file for keywords
check_relevance() {
    local file=$1
    local filename=$(basename "$file")
    
    # Core relevant keywords
    local relevant_keywords="water|utility|data center|rate|cost|EPWater|El Paso|Texas|development|agreement|statute|code|regulation|ledger|accountability"
    
    # Scraper/junk indicators
    local junk_keywords="reddit|twitter|social media|comment thread|upvote|downvote|karma|advertisement|cookie policy|terms of service"
    
    echo -e "\n${BLUE}Checking: $filename${NC}"
    
    # Count relevant vs junk
    relevant_count=$(grep -oiE "$relevant_keywords" "$file" | wc -l)
    junk_count=$(grep -oiE "$junk_keywords" "$file" | wc -l)
    
    echo "  Relevant mentions: $relevant_count"
    echo "  Junk indicators: $junk_count"
    
    if [ $junk_count -gt 10 ]; then
        echo -e "  ${YELLOW}⚠️  High junk content - consider removing${NC}"
        echo "$file" >> /tmp/docs-to-review.txt
    elif [ $relevant_count -lt 5 ]; then
        echo -e "  ${YELLOW}⚠️  Low relevance - verify usefulness${NC}"
        echo "$file" >> /tmp/docs-to-review.txt
    else
        echo -e "  ${GREEN}✓ Appears relevant${NC}"
    fi
}

# Clear review list
rm -f /tmp/docs-to-review.txt

# Check each markdown file
for file in "$DOCS_DIR"/*.md; do
    if [ -f "$file" ]; then
        check_relevance "$file"
    fi
done

echo -e "\n${YELLOW}Step 3: Files needing review${NC}"

if [ -f /tmp/docs-to-review.txt ]; then
    echo -e "${BLUE}These files may need cleanup:${NC}"
    cat /tmp/docs-to-review.txt
    echo ""
    echo -e "${YELLOW}Recommended actions:${NC}"
    echo "1. Review each file manually"
    echo "2. Remove scraped social media content"
    echo "3. Keep only source documents and analysis"
else
    echo -e "${GREEN}✓ No obvious junk files detected${NC}"
fi

echo -e "\n${YELLOW}Step 4: Recommended docs/ structure${NC}"

cat << 'EOF'

KEEP (High Value):
✅ legal-authorities.md        - TX/NM statutes
✅ epwater-ami-architecture.md - Technical specs
✅ comparable-jurisdictions.md - Precedent examples
✅ system-prompt-optimal.md    - CustomGPT config

REVIEW (Check relevance):
⚠️  Files from web scraping
⚠️  Reddit/social media scrapes
⚠️  Generic news articles
⚠️  Duplicate information

REMOVE (Low Value):
❌ Social media comments
❌ Advertisement content
❌ Cookie policies
❌ Unrelated jurisdictions
❌ Outdated information

EOF

echo -e "\n${YELLOW}Step 5: Create clean docs structure${NC}"

cat << 'EOF'

Recommended organization:

docs/
├── legal/                    # Primary sources
│   ├── texas-water-code.pdf
│   └── legal-authorities.md
├── precedents/              # Other cities
│   └── comparable-jurisdictions.md
├── technical/               # Specs
│   └── epwater-ami-architecture.md
├── config/                  # System
│   └── system-prompt-optimal.md
└── [Remove everything else unless verified useful]

EOF

echo -e "\n${GREEN}✓ Audit complete!${NC}"
echo "Review /tmp/docs-to-review.txt for files needing manual review"
