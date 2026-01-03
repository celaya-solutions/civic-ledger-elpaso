# 🎯 CIVIC LEDGER — SHIP IT NOW

**Status:** Ready to deploy → battle test → ship
**Time to ship:** ~95 minutes
**Current blocker:** Docs directory not in Docker container

---

## 🚨 THE ONE THING THAT'S BROKEN

Your server returns **500 Internal Server Error** on `/validate_citation` because:
- The `docs/` directory isn't being copied into the Docker container
- Your current `Dockerfile` has `COPY . .` but `.dockerignore` might be excluding docs
- The `CitationValidator` can't find `/app/docs/legal-authorities.md`

---

## ✅ THE FIX (3 Commands)

```bash
cd /Users/chriscelaya/Downloads/civic-ledger-elpaso

# 1. Make scripts executable
chmod +x deploy.sh battle-test.sh

# 2. Deploy (includes fix)
./deploy.sh

# 3. Battle test
./battle-test.sh
```

**That's it.** The `deploy.sh` script:
- Updates Dockerfile to explicitly copy docs
- Updates .dockerignore to not exclude docs
- Commits changes
- Deploys to Fly.io
- Tests endpoints
- Verifies docs in container

---

## 📋 WHAT HAPPENS NEXT

### After `./deploy.sh` succeeds:

**✅ Server is live:**
- https://civic-ledger-elpaso.fly.dev/
- All endpoints functional
- Docs accessible in container

### After `./battle-test.sh` passes:

**✅ All systems operational:**
- Root health check ✓
- OpenAPI schema ✓
- Citation validation ✓
- Feasibility checks ✓

### Then configure CustomGPT:

1. Go to https://chat.openai.com/ → "My GPTs"
2. Create/edit "Civic Ledger — El Paso Proof Engine"
3. Import actions from: `https://civic-ledger-elpaso.fly.dev/openapi.json`
4. Use system prompt from `CUSTOMGPT-SETUP.md`
5. Test with: "Validate that Texas Water Code Chapter 13 appears in legal-authorities.md"

### Then ship to community:

1. Push to GitHub: `git push origin main`
2. Post announcement to social media (draft in `CHECKLIST.md`)
3. Share example outputs
4. Monitor logs: `flyctl logs -a civic-ledger-elpaso`

---

## 📁 FILES CREATED FOR YOU

| File | Purpose |
|------|---------|
| `CHECKLIST.md` | Complete step-by-step deployment checklist |
| `DEPLOYMENT.md` | Manual deployment instructions + troubleshooting |
| `CUSTOMGPT-SETUP.md` | CustomGPT configuration guide with examples |
| `deploy.sh` | Automated deployment script |
| `battle-test.sh` | Automated testing script |
| `Dockerfile.fixed` | Fixed Dockerfile that includes docs |
| `.dockerignore.fixed` | Fixed .dockerignore that doesn't exclude docs |

---

## 🎬 START HERE

Open your terminal and run:

```bash
cd /Users/chriscelaya/Downloads/civic-ledger-elpaso
chmod +x deploy.sh battle-test.sh
./deploy.sh
```

**Expected output:**
```
🚀 Civic Ledger Deployment Script
==================================
Step 1: Verifying docs directory...
✓ Docs verified
Step 2: Updating Docker configuration...
✓ Dockerfile updated
✓ .dockerignore updated
Step 3: Checking git status...
Step 4: Committing changes...
Step 5: Deploying to Fly.io...
...
==================================
✓ Deployment Complete!
==================================
```

Then run:
```bash
./battle-test.sh
```

**Expected output:**
```
⚔️  Civic Ledger Battle Test
============================
✓ Root Health Check PASSED
✓ OpenAPI Schema PASSED
✓ Citation Validation PASSED
✓ Feasibility Check PASSED

🎉 All systems operational! Ready to ship.
```

---

## 🆘 IF SOMETHING BREAKS

### Server still returns 500:
```bash
flyctl ssh console -a civic-ledger-elpaso -C "ls -la /app/docs"
```
If docs are missing, redeploy:
```bash
./deploy.sh
```

### Build fails:
```bash
flyctl logs -a civic-ledger-elpaso
```
Look for errors, fix, redeploy.

### CustomGPT can't connect:
1. Test manually: `curl https://civic-ledger-elpaso.fly.dev/`
2. Check Fly.io status: `flyctl status -a civic-ledger-elpaso`
3. Restart: `flyctl apps restart civic-ledger-elpaso`

---

## 🚀 READY TO SHIP

Once `battle-test.sh` passes:

1. **Configure CustomGPT** (see `CUSTOMGPT-SETUP.md`)
2. **Push to GitHub:** `git push origin main`
3. **Ship to community** (see `CHECKLIST.md` Phase 5)

---

**Total time to ship:** ~95 minutes
**Current step:** Run `./deploy.sh`

**Let's go!** 🔥
