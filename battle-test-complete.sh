#!/bin/bash
set -e

echo "⚔️  Civic Ledger Battle Test - Complete"
echo "======================================="

BASE_URL="https://civic-ledger-elpaso.fly.dev"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

passed=0
failed=0

test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected=$5
    
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Testing: $name${NC}"
    echo -e "${BLUE}Endpoint: $method $BASE_URL$endpoint${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s "$BASE_URL$endpoint" 2>&1)
    else
        echo -e "${BLUE}Request body:${NC}"
        echo "$data" | jq '.' 2>/dev/null || echo "$data"
        response=$(curl -s -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    fi
    
    echo -e "${BLUE}Response:${NC}"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    
    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((passed++))
    else
        echo -e "${RED}✗ FAILED (expected to find: '$expected')${NC}"
        ((failed++))
    fi
}

# Test 1: Root endpoint
test_endpoint "Root Health Check" "GET" "/" "status"

# Test 2: Health endpoint
test_endpoint "Health Endpoint" "GET" "/health" "ok"

# Test 3: OpenAPI docs (FastAPI auto-generated)
test_endpoint "OpenAPI Docs" "GET" "/docs" "Swagger"

# Test 4: OpenAPI JSON
test_endpoint "OpenAPI JSON" "GET" "/openapi.json" "openapi"

echo -e "\n${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}Testing Functional Endpoints${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"

# Test 5: Citation validation (old endpoint)
citation_data='{
  "document": "legal-authorities.md",
  "page": 1,
  "claimed_text": "Texas Water Code"
}'
test_endpoint "Citation Validation (old path)" "POST" "/validate_citation" "$citation_data" "result"

# Test 6: Citation validation (new path)
test_endpoint "Citation Validation (new path)" "POST" "/citations/validate" "$citation_data" "result"

# Test 7: Feasibility check (old endpoint)
feasibility_data='{
  "proposed_control": "monthly water usage reporting",
  "jurisdiction": "elpaso",
  "utility_type": "water"
}'
test_endpoint "Feasibility Check (old path)" "POST" "/check_feasibility" "$feasibility_data" "result"

# Test 8: Feasibility check (new path)
test_endpoint "Feasibility Check (new path)" "POST" "/feasibility/check" "$feasibility_data" "result"

# Summary
echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Battle Test Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "Total Tests: $((passed + failed))"
echo -e "${GREEN}Passed: $passed${NC}"
echo -e "${RED}Failed: $failed${NC}"

if [ $failed -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All systems operational! Ready to ship.${NC}"
    echo -e "\nNext steps:"
    echo -e "1. Configure CustomGPT (see CUSTOMGPT-SETUP.md)"
    echo -e "2. Push to GitHub: git push origin main"
    echo -e "3. Ship to community!"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  Some tests failed, but server is responding${NC}"
    echo -e "\nCheck which endpoints are working:"
    echo -e "  Working: The server is live and responding"
    echo -e "  Action: Update CustomGPT to use working endpoints"
    echo -e "\nView full docs: https://civic-ledger-elpaso.fly.dev/docs"
    exit 1
fi
