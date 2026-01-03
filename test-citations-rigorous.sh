#!/bin/bash

echo "🧪 Rigorous Citation Testing Suite"
echo "===================================="

BASE_URL="https://civic-ledger-elpaso.fly.dev"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

passed=0
failed=0

# Test helper
test_citation() {
    local test_name=$1
    local document=$2
    local claimed_text=$3
    local should_find=$4  # "true" or "false"
    
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Test: $test_name${NC}"
    echo -e "${BLUE}Document: $document${NC}"
    echo -e "${BLUE}Looking for: \"$claimed_text\"${NC}"
    
    response=$(curl -s -X POST "$BASE_URL/citations/validate" \
        -H "Content-Type: application/json" \
        -d "{\"document\": \"$document\", \"claimed_text\": \"$claimed_text\"}")
    
    echo -e "${BLUE}Response:${NC}"
    echo "$response" | head -c 200
    echo ""
    
    if [ "$should_find" = "true" ]; then
        # Should find it
        if echo "$response" | grep -q "GREEN\|match"; then
            echo -e "${GREEN}✓ PASSED - Citation found as expected${NC}"
            ((passed++))
        else
            echo -e "${RED}✗ FAILED - Should have found citation but didn't${NC}"
            ((failed++))
        fi
    else
        # Should NOT find it
        if echo "$response" | grep -q "No matches\|not found"; then
            echo -e "${GREEN}✓ PASSED - Correctly reported no match${NC}"
            ((passed++))
        else
            echo -e "${RED}✗ FAILED - False positive (found something that doesn't exist)${NC}"
            ((failed++))
        fi
    fi
}

echo -e "\n${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}TEST SUITE 1: Known Good Citations${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"

# Test 1: Exact phrase that SHOULD exist
test_citation \
    "Exact match - Texas Water Code" \
    "legal-authorities.md" \
    "Texas Water Code" \
    "true"

# Test 2: Partial phrase that SHOULD exist
test_citation \
    "Partial match - utility regulation" \
    "legal-authorities.md" \
    "utility regulation" \
    "true"

# Test 3: Phrase that should NOT exist
test_citation \
    "False positive test - nonsense text" \
    "legal-authorities.md" \
    "purple monkey dishwasher" \
    "false"

# Test 4: Similar but wrong phrase
test_citation \
    "Near miss - wrong state code" \
    "legal-authorities.md" \
    "California Water Code" \
    "false"

echo -e "\n${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}TEST SUITE 2: Document Existence${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"

# Test 5: Non-existent document
test_citation \
    "Missing document test" \
    "nonexistent-file.md" \
    "any text" \
    "false"

# Test 6: Real document with real content
test_citation \
    "EPWater AMI reference" \
    "epwater-ami-architecture.md" \
    "AMI" \
    "true"

echo -e "\n${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}TEST SUITE 3: Edge Cases${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"

# Test 7: Very short query
test_citation \
    "Single word query" \
    "legal-authorities.md" \
    "Texas" \
    "true"

# Test 8: Case sensitivity
test_citation \
    "Case insensitive match" \
    "legal-authorities.md" \
    "TEXAS WATER CODE" \
    "true"

# Summary
echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Test Results Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "Total Tests: $((passed + failed))"
echo -e "${GREEN}Passed: $passed${NC}"
echo -e "${RED}Failed: $failed${NC}"

if [ $failed -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All citation tests passed!${NC}"
    echo -e "Citation validation is working correctly."
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed${NC}"
    echo -e "Review citation_validator.py implementation"
    exit 1
fi
