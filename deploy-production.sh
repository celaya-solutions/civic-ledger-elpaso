#!/bin/bash
set -e

echo "🚀 Civic Ledger Production Deployment"
echo "======================================"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if we're in the right directory
if [ ! -f "server.py" ]; then
    echo -e "${RED}Error: Must run from civic-ledger-elpaso root${NC}"
    exit 1
fi

# Step 1: Backup current server
echo -e "\n${YELLOW}Step 1: Backing up current server.py...${NC}"
if [ -f "server.py" ]; then
    cp server.py server.py.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✓ Backup created${NC}"
fi

# Step 2: Use complete server implementation
echo -e "\n${YELLOW}Step 2: Installing production server...${NC}"
if [ -f "server_complete.py" ]; then
    cp server_complete.py server.py
    echo -e "${GREEN}✓ Production server installed${NC}"
else
    echo -e "${RED}Error: server_complete.py not found${NC}"
    exit 1
fi

# Step 3: Verify docs exist
echo -e "\n${YELLOW}Step 3: Verifying docs directory...${NC}"
if [ ! -d "docs" ]; then
    echo -e "${RED}Error: docs/ directory not found${NC}"
    exit 1
fi

# Count docs
doc_count=$(find docs -type f \( -name "*.md" -o -name "*.pdf" \) | wc -l)
echo -e "${GREEN}✓ Found $doc_count documents in docs/${NC}"

# Step 4: Update Dockerfile
echo -e "\n${YELLOW}Step 4: Updating Dockerfile...${NC}"
if [ -f "Dockerfile.fixed" ]; then
    cp Dockerfile Dockerfile.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
    cp Dockerfile.fixed Dockerfile
    echo -e "${GREEN}✓ Dockerfile updated${NC}"
fi

# Step 5: Update .dockerignore
echo -e "\n${YELLOW}Step 5: Updating .dockerignore...${NC}"
if [ -f ".dockerignore.fixed" ]; then
    cp .dockerignore .dockerignore.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
    cp .dockerignore.fixed .dockerignore
    echo -e "${GREEN}✓ .dockerignore updated${NC}"
fi

# Step 6: Save OpenAPI spec
echo -e "\n${YELLOW}Step 6: Installing OpenAPI spec...${NC}"
if [ -f "openapi.yaml" ]; then
    echo -e "${GREEN}✓ OpenAPI spec ready${NC}"
else
    echo -e "${YELLOW}⚠ OpenAPI spec not found - CustomGPT will use /docs${NC}"
fi

# Step 7: Git status
echo -e "\n${YELLOW}Step 7: Git status...${NC}"
git status --short

# Step 8: Commit
echo -e "\n${YELLOW}Step 8: Committing changes...${NC}"
read -p "Commit message (Enter for default): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="feat: Production deployment with full OpenAPI implementation"
fi

git add server.py Dockerfile .dockerignore openapi.yaml 2>/dev/null || true
git commit -m "$commit_msg" || echo "No changes to commit"

# Step 9: Deploy to Fly.io
echo -e "\n${YELLOW}Step 9: Deploying to Fly.io...${NC}"
flyctl deploy --app civic-ledger-elpaso

# Step 10: Wait for deployment
echo -e "\n${YELLOW}Step 10: Waiting for deployment...${NC}"
sleep 15

# Step 11: Test endpoints
echo -e "\n${YELLOW}Step 11: Testing endpoints...${NC}"

echo "Testing /health..."
curl -s https://civic-ledger-elpaso.fly.dev/health | jq '.'

echo -e "\nTesting /citations/validate..."
curl -s -X POST "https://civic-ledger-elpaso.fly.dev/citations/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "legal-authorities.md",
    "claimed_text": "Texas Water Code"
  }' | jq '.'

# Step 12: Verify in container
echo -e "\n${YELLOW}Step 12: Verifying docs in container...${NC}"
flyctl ssh console -a civic-ledger-elpaso -C "ls -la /app/docs | head -10"

echo -e "\n${GREEN}======================================"
echo -e "✓ Production Deployment Complete!"
echo -e "======================================${NC}"
echo -e "\nAPI URLs:"
echo -e "  Base: ${GREEN}https://civic-ledger-elpaso.fly.dev${NC}"
echo -e "  Docs: ${GREEN}https://civic-ledger-elpaso.fly.dev/docs${NC}"
echo -e "  Health: ${GREEN}https://civic-ledger-elpaso.fly.dev/health${NC}"
echo -e "\nOpenAPI Spec:"
echo -e "  ${GREEN}https://civic-ledger-elpaso.fly.dev/openapi.json${NC}"
echo -e "\nNext Steps:"
echo -e "  1. Configure CustomGPT (see CUSTOMGPT-SETUP.md)"
echo -e "  2. Run battle test: ./battle-test.sh"
echo -e "  3. Push to GitHub: git push origin main"
echo -e "  4. Ship to community!"
