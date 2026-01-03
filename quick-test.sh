#!/bin/bash

echo "🔍 Quick Endpoint Test"
echo "====================="

BASE_URL="https://civic-ledger-elpaso.fly.dev"

echo -e "\n1. Root (/) ..."
curl -s "$BASE_URL/" | jq '.'

echo -e "\n2. Health (/health) ..."
curl -s "$BASE_URL/health" | jq '.'

echo -e "\n3. OpenAPI JSON (/openapi.json) ..."
curl -s "$BASE_URL/openapi.json" | jq '.info.title'

echo -e "\n4. Citation Validation (/citations/validate) ..."
curl -s -X POST "$BASE_URL/citations/validate" \
  -H "Content-Type: application/json" \
  -d '{"document": "legal-authorities.md", "claimed_text": "Texas"}' \
  | jq '.'

echo -e "\n5. Feasibility Check (/feasibility/check) ..."
curl -s -X POST "$BASE_URL/feasibility/check" \
  -H "Content-Type: application/json" \
  -d '{
    "proposed_control": "Monthly water reporting",
    "jurisdiction": "elpaso",
    "utility_type": "water"
  }' | jq '.'

echo -e "\n✅ Quick test complete!"
echo "View full docs at: https://civic-ledger-elpaso.fly.dev/docs"
