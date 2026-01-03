#!/bin/bash
set -e

echo "🔧 Quick Dockerfile Fix"
echo "======================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd /Users/chriscelaya/Downloads/civic-ledger-elpaso

echo -e "${YELLOW}Committing Dockerfile fix...${NC}"
git add Dockerfile
git commit -m "fix: Remove civic-server copy from Dockerfile (it's a venv)" || echo "Already committed"

echo -e "\n${YELLOW}Deploying to Fly.io...${NC}"
flyctl deploy --app civic-ledger-elpaso

echo -e "\n${YELLOW}Waiting for deployment...${NC}"
sleep 10

echo -e "\n${GREEN}Testing endpoints...${NC}"
echo "Testing /health..."
curl -s https://civic-ledger-elpaso.fly.dev/health | jq '.'

echo -e "\nTesting /citations/validate..."
curl -s -X POST "https://civic-ledger-elpaso.fly.dev/citations/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "legal-authorities.md",
    "claimed_text": "Texas Water Code"
  }' | jq '.'

echo -e "\n${GREEN}✓ Deployment complete!${NC}"
echo "Run ./battle-test.sh to verify all endpoints"
