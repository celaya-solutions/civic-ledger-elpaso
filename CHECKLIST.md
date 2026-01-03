# 🎯 Civic Ledger Deployment Checklist

**Objective:** Deploy functioning CustomGPT + server on Fly.io, battle test, push to git, ship to El Paso community

---

## Pre-Flight Checks

- [ ] Server files exist locally at `/Users/chriscelaya/Downloads/civic-ledger-elpaso`
- [ ] Fly.io CLI installed (`flyctl version`)
- [ ] Authenticated to Fly.io (`flyctl auth whoami`)
- [ ] Git repository initialized and tracked
- [ ] `docs/` directory exists with `legal-authorities.md`

---

## Phase 1: Fix & Deploy Server (30 min)

### 1.1 Apply Fixes
```bash
cd /Users/chriscelaya/Downloads/civic-ledger-elpaso

# Make scripts executable
chmod +x deploy.sh battle-test.sh

# Verify docs exist
ls -la docs/legal-authorities.md
```

**Checkpoint:**
- [ ] `deploy.sh` is executable
- [ ] `battle-test.sh` is executable
- [ ] `docs/legal-authorities.md` exists

### 1.2 Deploy to Fly.io
```bash
./deploy.sh
```

**What this does:**
1. Verifies docs directory
2. Updates Dockerfile to include docs
3. Updates .dockerignore to not exclude docs
4. Commits changes to git
5. Deploys to Fly.io
6. Tests endpoints
7. Verifies docs in container

**Checkpoint:**
- [ ] Build succeeds without errors
- [ ] Deployment completes
- [ ] Root endpoint returns `{"status":"ok"}`
- [ ] OpenAPI schema accessible
- [ ] Docs directory exists in container

### 1.3 Battle Test
```bash
./battle-test.sh
```

**Expected Results:**
```
⚔️  Civic Ledger Battle Test
============================
✓ Root Health Check PASSED
✓ OpenAPI Schema PASSED
✓ Citation Validation PASSED
✓ Feasibility Check PASSED

Battle Test Results:
Passed: 4
Failed: 0
🎉 All systems operational! Ready to ship.
```

**Checkpoint:**
- [ ] All 4 tests pass
- [ ] No 500 errors on `/validate_citation`
- [ ] Server logs show no errors

---

## Phase 2: Configure CustomGPT (20 min)

### 2.1 Access CustomGPT Builder
1. Go to https://chat.openai.com/
2. Click profile → "My GPTs"
3. Create new GPT or edit existing "Civic Ledger"

**Checkpoint:**
- [ ] CustomGPT builder open

### 2.2 Configure Basic Info
- **Name:** `Civic Ledger — El Paso Proof Engine`
- **Description:** 
  ```
  Production-ready tool for proof-based civic accountability in El Paso, TX. 
  Generates policy documents, records requests, and accountability frameworks 
  with verifiable citations and feasibility checks. Built by Celaya Solutions.
  ```
- **Instructions:** Use content from `CUSTOMGPT-SETUP.md` (system prompt section)

**Checkpoint:**
- [ ] Name set
- [ ] Description added
- [ ] Instructions pasted

### 2.3 Add Actions
Click "Create new action" → "Import from URL":
```
https://civic-ledger-elpaso.fly.dev/openapi.json
```

Or manually add these three actions:
1. **validateCitation** - POST /validate_citation
2. **checkFeasibility** - POST /check_feasibility
3. **searchLegalAuthority** - POST /search_legal_authority

**Checkpoint:**
- [ ] All 3 actions imported
- [ ] Action endpoints correct
- [ ] Authentication set to "None"
- [ ] Test actions work from builder

### 2.4 Configure Conversation Starters
Add these example prompts:
```
Generate a staff checklist for data center water ledger
Validate that Texas Water Code Chapter 13 addresses utility rates
Check if El Paso Water can implement monthly reporting
Create a resident-facing explainer for water accountability
```

**Checkpoint:**
- [ ] 4 conversation starters added

---

## Phase 3: Test CustomGPT Integration (15 min)

### 3.1 Test Citation Validation
Ask CustomGPT:
```
Validate that "Texas Water Code Chapter 13" appears in legal-authorities.md
```

**Expected:**
- Uses `validateCitation` action
- Returns GREEN confidence
- Shows exact match details

**Checkpoint:**
- [ ] Action called successfully
- [ ] Returns valid JSON response
- [ ] No 500 errors

### 3.2 Test Feasibility Check
Ask CustomGPT:
```
Check if El Paso Water can implement monthly data center water usage reporting
```

**Expected:**
- Uses `checkFeasibility` action
- Assesses AMI infrastructure capabilities
- Returns feasibility verdict

**Checkpoint:**
- [ ] Action called successfully
- [ ] Returns feasibility assessment
- [ ] No errors

### 3.3 Test Full Workflow
Ask CustomGPT:
```
Generate a 1-page staff checklist for implementing a data center water ledger in El Paso
```

**Expected:**
- Uses multiple actions
- Validates citations
- Checks feasibility
- Generates formatted output

**Checkpoint:**
- [ ] Multiple actions used
- [ ] Output includes citations
- [ ] Output includes feasibility notes
- [ ] Format is clean and usable

---

## Phase 4: Push to GitHub (10 min)

### 4.1 Verify Git Status
```bash
git status
```

**Checkpoint:**
- [ ] All changes staged
- [ ] Commit messages clear

### 4.2 Push to Remote
```bash
git push origin main
```

**Checkpoint:**
- [ ] Push succeeds
- [ ] GitHub repo updated
- [ ] README.md visible
- [ ] CUSTOMGPT-SETUP.md visible

---

## Phase 5: Ship to El Paso Community (20 min)

### 5.1 Prepare Announcement Post
**Platform:** Twitter/X, LinkedIn, Facebook

**Sample Post:**
```
🚨 NEW TOOL: Civic Ledger — El Paso Proof Engine

Generate verifiable accountability frameworks for El Paso data centers with:
✅ Validated citations from legal sources
✅ Feasibility checks for proposed controls
✅ Policy templates for staff & residents

Built by @CelayaSolutions using AI + open data

Try it: [CustomGPT link]
Learn more: https://github.com/celaya-solutions/civic-ledger-elpaso

#ElPaso #CivicTech #DataCenters #OpenGov
```

**Checkpoint:**
- [ ] Post drafted
- [ ] Links verified
- [ ] Hashtags added

### 5.2 Share Example Outputs
Create 2-3 example documents using CustomGPT:
1. Staff checklist for water ledger
2. Resident explainer for utility impacts
3. Records request template

**Checkpoint:**
- [ ] 3 examples generated
- [ ] Examples saved as markdown
- [ ] Examples added to `examples/` directory
- [ ] Examples pushed to GitHub

### 5.3 Post to Community
Share on:
- [ ] Twitter/X
- [ ] LinkedIn
- [ ] Facebook (El Paso groups)
- [ ] Reddit (r/ElPaso)
- [ ] Nextdoor (if applicable)

**Checkpoint:**
- [ ] Posted to at least 3 platforms
- [ ] Links work
- [ ] CustomGPT is publicly accessible

---

## Phase 6: Monitor & Iterate (Ongoing)

### 6.1 Monitor Logs
```bash
flyctl logs -a civic-ledger-elpaso
```

**Watch for:**
- 500 errors
- Unusual traffic patterns
- Action failures

**Checkpoint:**
- [ ] Logs reviewed
- [ ] No critical errors

### 6.2 Respond to Feedback
- [ ] Check GitHub issues
- [ ] Respond to social media comments
- [ ] Track usage patterns

### 6.3 Iterate Based on Usage
- [ ] Note common questions
- [ ] Identify missing features
- [ ] Plan v1.1 updates

---

## Success Criteria

✅ **Server Deployed:**
- Fly.io app running
- All endpoints functional
- Docs accessible in container
- Zero 500 errors

✅ **CustomGPT Configured:**
- Actions connected
- Test prompts work
- Output quality good
- No authentication errors

✅ **Code Shipped:**
- GitHub repo updated
- README clear
- Examples included
- License added

✅ **Community Engaged:**
- Posted to 3+ platforms
- Example outputs shared
- CustomGPT link public
- Ready for feedback

---

## Rollback Plan

If critical issues arise:

1. **Revert Deployment:**
   ```bash
   mv Dockerfile.backup Dockerfile
   flyctl deploy --app civic-ledger-elpaso
   ```

2. **Disable CustomGPT:**
   - Edit GPT → Make private
   - Remove actions temporarily

3. **Fix Issues:**
   - Review logs
   - Test locally
   - Redeploy when fixed

---

## Time Estimate

| Phase | Est. Time | Status |
|-------|-----------|--------|
| Fix & Deploy | 30 min | ⏳ |
| Configure CustomGPT | 20 min | ⏳ |
| Test Integration | 15 min | ⏳ |
| Push to GitHub | 10 min | ⏳ |
| Ship to Community | 20 min | ⏳ |
| **Total** | **95 min** | |

---

**Let's ship this! 🚀**

Start with Phase 1, Step 1.1. Run the commands and check off each item as you go.
