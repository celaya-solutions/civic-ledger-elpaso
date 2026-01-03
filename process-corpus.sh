#!/bin/bash

echo "🔄 Process dc_corpus Materials"
echo "=============================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="/Users/chriscelaya/Downloads/civic-ledger-elpaso"
CORPUS_DIR="$PROJECT_ROOT/dc_corpus"
DOCS_DIR="$PROJECT_ROOT/docs"

if [ ! -d "$CORPUS_DIR" ]; then
    echo -e "${YELLOW}⚠️  dc_corpus not found at $CORPUS_DIR${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Analyzing dc_corpus contents...${NC}"

# Function to categorize and move files
process_files() {
    local source_dir=$1
    local file_type=$2
    
    find "$source_dir" -type f -name "*.$file_type" 2>/dev/null | while read -r file; do
        filename=$(basename "$file")
        
        # Categorize based on filename patterns
        if echo "$filename" | grep -iq "water.*code\|statute\|regulation"; then
            dest="$DOCS_DIR/legal/"
            category="Legal Authority"
        elif echo "$filename" | grep -iq "board.*minute\|council.*minute"; then
            dest="$DOCS_DIR/board-minutes/"
            category="Board Minutes"
        elif echo "$filename" | grep -iq "development.*agreement\|dev.*agreement"; then
            dest="$DOCS_DIR/development-agreements/"
            category="Development Agreement"
        elif echo "$filename" | grep -iq "cost.*study\|rate.*study"; then
            dest="$DOCS_DIR/cost-studies/"
            category="Cost Study"
        elif echo "$filename" | grep -iq "loudoun\|mesa\|raleigh"; then
            jurisdiction=$(echo "$filename" | grep -io "loudoun\|mesa\|raleigh" | head -1 | tr '[:upper:]' '[:lower:]')
            dest="$DOCS_DIR/precedents/$jurisdiction/"
            mkdir -p "$dest"
            category="Precedent ($jurisdiction)"
        else
            dest="$DOCS_DIR/technical-specs/"
            category="Technical/Other"
        fi
        
        mkdir -p "$dest"
        echo -e "${BLUE}[$category]${NC} $filename → ${dest}"
        # Uncomment to actually move files:
        # cp "$file" "$dest"
    done
}

# Process PDFs
echo -e "\n${YELLOW}PDFs found:${NC}"
process_files "$CORPUS_DIR" "pdf"

# Process HTML
echo -e "\n${YELLOW}HTML files found:${NC}"
html_count=$(find "$CORPUS_DIR" -name "*.html" 2>/dev/null | wc -l)
echo "Total HTML files: $html_count"
echo "(HTML files need conversion to PDF or MD before adding to docs/)"

# Process JSONL files
echo -e "\n${YELLOW}Structured data found:${NC}"
for jsonl in "$CORPUS_DIR"/*.jsonl; do
    if [ -f "$jsonl" ]; then
        count=$(wc -l < "$jsonl")
        echo "  $(basename $jsonl): $count records"
    fi
done

echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Summary & Next Steps${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

cat << 'EOF'

WHAT WE FOUND:
- Check the categorization above
- Files are PREVIEWED only (not moved yet)

TO ACTUALLY PROCESS FILES:
1. Review the categorization output above
2. Edit this script and uncomment the 'cp' line
3. Run again to move files to docs/

CONVERT HTML TO DOCS:
- Use Pandoc: pandoc file.html -o file.pdf
- Or extract text: python extract-html-text.py

PROCESS JSONL DATA:
- Extract relevant records
- Convert to markdown summaries
- Add to appropriate docs/ subdirectories

EOF

echo -e "\n${GREEN}✓ Analysis complete!${NC}"
echo "Review output and modify script to move files."
