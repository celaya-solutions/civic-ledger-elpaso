# 🚀 Deployment Guide

## Quick Deploy (3 commands)

```bash
# 1. Make scripts executable
chmod +x deploy.sh battle-test.sh

# 2. Deploy to Fly.io
./deploy.sh

# 3. Battle test
./battle-test.sh
```

---

## What Each Script Does

### `deploy.sh`
- Verifies docs directory exists
- Updates Dockerfile and .dockerignore
- Commits changes to git
- Deploys to Fly.io
- Tests deployed endpoints
- Verifies docs in container

### `battle-test.sh`
- Tests all API endpoints
- Validates responses
- Reports pass/fail summary
- Returns exit code (0 = success)

---

## Manual Deployment Steps

If you prefer manual control:

### 1. Update Docker Configuration
```bash
mv Dockerfile.fixed Dockerfile
mv .dockerignore.fixed .dockerignore
```

### 2. Commit Changes
```bash
git add Dockerfile .dockerignore
git commit -m "fix: Include docs directory in Docker build"
```

### 3. Deploy
```bash
flyctl deploy --app civic-ledger-elpaso
```

### 4. Test
```bash
# Health check
curl https://civic-ledger-elpaso.fly.dev/

# Test citation validation
curl -X POST https://civic-ledger-elpaso.fly.dev/validate_citation \
  -H "Content-Type: application/json" \
  -d '{
    "document": "legal-authorities.md",
    "page": 1,
    "claimed_text": "Texas Water Code Chapter 13"
  }'
```

### 5. Verify docs in container
```bash
flyctl ssh console -a civic-ledger-elpaso -C "ls -la /app/docs"
```

---

## Troubleshooting

### Server returns 500 on /validate_citation

**Diagnosis:**
```bash
flyctl logs -a civic-ledger-elpaso
```

Look for:
- `FileNotFoundError: [Errno 2] No such file or directory: '/app/docs/legal-authorities.md'`
- `TypeError: unsupported operand type(s) for /: 'str' and 'str'`

**Fix:**
```bash
# SSH into container
flyctl ssh console -a civic-ledger-elpaso

# Check if docs exist
ls /app/docs

# If missing, redeploy with fixed Dockerfile
./deploy.sh
```

### Build fails

**Check .dockerignore:**
```bash
cat .dockerignore
```

Make sure it does NOT contain:
```
docs/
```

### Can't connect to Fly.io

**Check status:**
```bash
flyctl status -a civic-ledger-elpaso
```

**Restart app:**
```bash
flyctl apps restart civic-ledger-elpaso
```

---

## Next Steps After Successful Deployment

1. **Configure CustomGPT**
   - See `CUSTOMGPT-SETUP.md` for detailed instructions
   - Import OpenAPI schema from https://civic-ledger-elpaso.fly.dev/openapi.json

2. **Test with CustomGPT**
   - Ask it to validate citations
   - Request feasibility checks
   - Generate policy documents

3. **Push to GitHub**
   ```bash
   git push origin main
   ```

4. **Share with El Paso Community**
   - Post on social networks
   - Share example outputs
   - Invite community testing

---

## Monitoring

### Real-time logs
```bash
flyctl logs -a civic-ledger-elpaso
```

### Check resource usage
```bash
flyctl status -a civic-ledger-elpaso
```

### Scale if needed
```bash
flyctl scale count 2 -a civic-ledger-elpaso
```

---

## Rollback

If deployment breaks:

```bash
# Restore previous Dockerfile
mv Dockerfile.backup Dockerfile
mv .dockerignore.backup .dockerignore

# Redeploy
flyctl deploy --app civic-ledger-elpaso
```

---

**Need Help?**
- Review logs: `flyctl logs -a civic-ledger-elpaso`
- Check docs: https://fly.io/docs/
- Contact: chris@chriscelaya.com
