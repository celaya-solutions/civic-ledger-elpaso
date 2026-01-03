#!/bin/bash
set -e

echo "🚀 Civic Ledger Deployment Script"
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "server.py" ]; then
    echo -e "${RED}Error: Must run from civic-ledger-elpaso root directory${NC}"
    exit 1
fi

# Step 1: Verify docs exist
echo -e "\n${YELLOW}Step 1: Verifying docs directory...${NC}"
if [ ! -d "docs" ]; then
    echo -e "${RED}Error: docs/ directory not found${NC}"
    exit 1
fi
if [ ! -f "docs/legal-authorities.md" ]; then
    echo -e "${RED}Error: docs/legal-authorities.md not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docs verified${NC}"

# Step 2: Replace Dockerfile and .dockerignore
echo -e "\n${YELLOW}Step 2: Updating Docker configuration...${NC}"
if [ -f "Dockerfile.fixed" ]; then
    mv Dockerfile Dockerfile.backup
    mv Dockerfile.fixed Dockerfile
    echo -e "${GREEN}✓ Dockerfile updated${NC}"
fi
if [ -f ".dockerignore.fixed" ]; then
    mv .dockerignore .dockerignore.backup
    mv .dockerignore.fixed .dockerignore
    echo -e "${GREEN}✓ .dockerignore updated${NC}"
fi

# Step 3: Git status check
echo -e "\n${YELLOW}Step 3: Checking git status...${NC}"
git status --short

# Step 4: Commit changes
echo -e "\n${YELLOW}Step 4: Committing changes...${NC}"
read -p "Commit message (or press Enter for default): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="fix: Include docs directory in Docker build for Fly.io deployment"
fi
git add Dockerfile .dockerignore
git commit -m "$commit_msg" || echo "No changes to commit"

# Step 5: Deploy to Fly.io
echo -e "\n${YELLOW}Step 5: Deploying to Fly.io...${NC}"
flyctl deploy --app civic-ledger-elpaso

# Step 6: Wait for deployment
echo -e "\n${YELLOW}Step 6: Waiting for deployment to stabilize...${NC}"
sleep 10

# Step 7: Test endpoints
echo -e "\n${YELLOW}Step 7: Testing deployed endpoints...${NC}"

echo -e "\nTesting root endpoint..."
curl -s https://civic-ledger-elpaso.fly.dev/ | jq '.'

echo -e "\nTesting /validate_citation endpoint..."
curl -s -X POST "https://civic-ledger-elpaso.fly.dev/validate_citation" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "legal-authorities.md",
    "page": 1,
    "claimed_text": "Texas Water Code Chapter 13"
  }' | jq '.'

# Step 8: SSH into container to verify docs
echo -e "\n${YELLOW}Step 8: Verifying docs in container...${NC}"
flyctl ssh console -a civic-ledger-elpaso -C "ls -la /app/docs"

echo -e "\n${GREEN}=================================="
echo -e "✓ Deployment Complete!"
echo -e "==================================${NC}"
echo -e "\nAPI Base URL: ${GREEN}https://civic-ledger-elpaso.fly.dev${NC}"
echo -e "OpenAPI Docs: ${GREEN}https://civic-ledger-elpaso.fly.dev/docs${NC}"
echo -e "\nNext steps:"
echo -e "1. Configure CustomGPT to use this server"
echo -e "2. Test all endpoints via CustomGPT interface"
echo -e "3. Push to GitHub: git push origin main"
