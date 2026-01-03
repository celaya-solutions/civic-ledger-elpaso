#!/bin/bash
set -e

# Battle Test Script for Civic Ledger
# Run this after deployment to verify everything works

echo "⚔️  Civic Ledger Battle Test"
echo "============================"

BASE_URL="https://civic-ledger-elpaso.fly.dev"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

passed=0
failed=0

test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected=$5
    
    echo -e "\n${YELLOW}Testing: $name${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s "$BASE_URL$endpoint")
    else
        response=$(curl -s -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((passed++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "Response: $response"
        ((failed++))
    fi
}

echo -e "\n${YELLOW}Running health checks...${NC}"

# Test 1: Root endpoint
test_endpoint "Root Health Check" "GET" "/" "ok"

# Test 2: OpenAPI schema
test_endpoint "OpenAPI Schema" "GET" "/openapi.json" "openapi"

echo -e "\n${YELLOW}Running functional tests...${NC}"

# Test 3: Citation validation
citation_data='{
  "document": "legal-authorities.md",
  "page": 1,
  "claimed_text": "Texas Water Code Chapter 13"
}'
test_endpoint "Citation Validation" "POST" "/validate_citation" "$citation_data" "citations"

# Test 4: Feasibility check
feasibility_data='{
  "proposed_control": "monthly water usage reporting",
  "jurisdiction": "el-paso-tx",
  "utility_type": "water"
}'
test_endpoint "Feasibility Check" "POST" "/check_feasibility" "$feasibility_data" "feasible"

# Summary
echo -e "\n============================"
echo -e "Battle Test Results:"
echo -e "${GREEN}Passed: $passed${NC}"
echo -e "${RED}Failed: $failed${NC}"
echo "============================"

if [ $failed -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All systems operational! Ready to ship.${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed. Review logs and redeploy.${NC}"
    echo "Run: flyctl logs -a civic-ledger-elpaso"
    exit 1
fi
