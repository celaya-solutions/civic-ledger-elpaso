#!/bin/bash

echo "🔍 Civic Ledger Endpoint Discovery"
echo "==================================="

BASE_URL="https://civic-ledger-elpaso.fly.dev"

echo -e "\n📋 Checking available endpoints..."
echo -e "\n1. Getting OpenAPI schema..."

curl -s "$BASE_URL/openapi.json" | jq -r '.paths | keys[]' 2>/dev/null | sort

echo -e "\n2. FastAPI Docs UI available at:"
echo "   → https://civic-ledger-elpaso.fly.dev/docs"

echo -e "\n3. Testing each endpoint type..."

# Test old-style endpoints
echo -e "\n━━━ OLD STYLE ENDPOINTS ━━━"
echo "POST /validate_citation:"
curl -s -X POST "$BASE_URL/validate_citation" \
  -H "Content-Type: application/json" \
  -d '{"document": "legal-authorities.md", "claimed_text": "Texas"}' 2>&1 | head -5

echo -e "\nPOST /check_feasibility:"
curl -s -X POST "$BASE_URL/check_feasibility" \
  -H "Content-Type: application/json" \
  -d '{"proposed_control": "test", "jurisdiction": "elpaso", "utility_type": "water"}' 2>&1 | head -5

# Test new-style endpoints  
echo -e "\n━━━ NEW STYLE ENDPOINTS ━━━"
echo "POST /citations/validate:"
curl -s -X POST "$BASE_URL/citations/validate" \
  -H "Content-Type: application/json" \
  -d '{"document": "legal-authorities.md", "claimed_text": "Texas"}' 2>&1 | head -5

echo -e "\nPOST /feasibility/check:"
curl -s -X POST "$BASE_URL/feasibility/check" \
  -H "Content-Type: application/json" \
  -d '{"proposed_control": "test", "jurisdiction": "elpaso", "utility_type": "water"}' 2>&1 | head -5

echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Check which endpoints returned 200 vs 404"
echo "   Visit https://civic-ledger-elpaso.fly.dev/docs to see all available endpoints"
