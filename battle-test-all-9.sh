#!/bin/bash
set -e

echo "⚔️  Civic Ledger Battle Test - All 9 Endpoints"
echo "=============================================="

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
    
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Testing: $name${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$BASE_URL$endpoint" 2>&1)
    else
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    fi
    
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | grep -v "HTTP_STATUS")
    
    # Show first 150 chars of response
    echo "$body" | cut -c1-150
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ PASSED (HTTP $http_code)${NC}"
        ((passed++))
    else
        echo -e "${RED}✗ FAILED (HTTP $http_code)${NC}"
        ((failed++))
    fi
}

echo -e "\n${YELLOW}═══ HEALTH CHECKS ═══${NC}"

test_endpoint "1. Root Health" "GET" "/" ""
test_endpoint "2. Health Endpoint" "GET" "/health" ""

echo -e "\n${YELLOW}═══ ALL 9 PRODUCTION ENDPOINTS ═══${NC}"

test_endpoint "3. Legal Authority Search" "POST" "/legal/search" '{
  "jurisdiction": "texas",
  "topic": "utility_regulation",
  "query": "What powers do cities have over utility rates?"
}'

test_endpoint "4. Citation Validation" "POST" "/citations/validate" '{
  "document": "legal-authorities.md",
  "claimed_text": "Texas Water Code"
}'

test_endpoint "5. Load Precedent" "POST" "/precedents/load" '{
  "jurisdiction": "loudoun_county",
  "document_type": "development_agreement",
  "topic": "infrastructure_escrow"
}'

test_endpoint "6. Generate Records Request" "POST" "/records-request/generate" '{
  "jurisdiction": "epwater",
  "document_type": "cost_study",
  "date_range": "2024-01-01 to 2024-12-31",
  "specific_topic": "Data center water usage"
}'

test_endpoint "7. Check Feasibility" "POST" "/feasibility/check" '{
  "proposed_control": "Monthly aggregated water usage reporting",
  "jurisdiction": "elpaso",
  "utility_type": "water"
}'

test_endpoint "8. Assemble Policy Packet" "POST" "/policy-packet/assemble" '{
  "packet_type": "council_presentation",
  "components": ["one_page_checklist", "resident_explainer"],
  "jurisdiction": "city_of_elpaso"
}'

test_endpoint "9. Extract Board Minutes" "POST" "/board-minutes/extract" '{
  "document": "legal-authorities.md",
  "search_terms": ["water", "rate", "cost"],
  "date_range": "2024-01-01 to 2024-12-31"
}'

test_endpoint "10. Cost-Benefit Calculator" "POST" "/cost-benefit/calculate" '{
  "control_type": "independent_audit",
  "scope": "system_wide",
  "jurisdiction": "elpaso"
}'

# Summary
echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Battle Test Summary - 10 Endpoints${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "Total Tests: $((passed + failed))"
echo -e "${GREEN}Passed: $passed${NC}"
echo -e "${RED}Failed: $failed${NC}"

percent=$((passed * 100 / (passed + failed)))

if [ $passed -ge 8 ]; then
    echo -e "\n${GREEN}🎉 Server is operational! ($percent% success rate)${NC}"
    echo -e "\n${YELLOW}Next Steps:${NC}"
    echo -e "1. ✅ Configure CustomGPT"
    echo -e "   → Import from: https://civic-ledger-elpaso.fly.dev/openapi.json"
    echo -e "2. ✅ Test with CustomGPT prompts"
    echo -e "3. ✅ Push to GitHub: git push origin main"
    echo -e "4. ✅ Ship to El Paso community!"
    echo -e "\n${BLUE}API Docs: https://civic-ledger-elpaso.fly.dev/docs${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  Server responding but some endpoints need work${NC}"
    echo -e "Working endpoints: $passed/$((passed + failed))"
    echo -e "\nYou can still configure CustomGPT with working endpoints!"
    echo -e "\n${BLUE}API Docs: https://civic-ledger-elpaso.fly.dev/docs${NC}"
    exit 1
fi
