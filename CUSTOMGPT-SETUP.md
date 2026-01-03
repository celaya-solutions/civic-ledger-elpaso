# CustomGPT Configuration Guide

## 🎯 Objective
Connect your CustomGPT to the deployed Civic Ledger MCP server on Fly.io

---

## 📡 Server Details

**Base URL:** `https://civic-ledger-elpaso.fly.dev`

**API Status:** Check at https://civic-ledger-elpaso.fly.dev/

**OpenAPI Schema:** https://civic-ledger-elpaso.fly.dev/openapi.json

---

## 🔧 CustomGPT Actions Setup

### Step 1: Access CustomGPT Builder
1. Go to https://chat.openai.com/
2. Click your profile → "My GPTs"
3. Find "Civic Ledger — El Paso Proof Engine" (or create new)
4. Click "Edit"

### Step 2: Configure Actions

Click "Create new action" and paste this OpenAPI schema URL:

```
https://civic-ledger-elpaso.fly.dev/openapi.json
```

Or manually define these actions:

#### Action 1: Validate Citation
```yaml
operationId: validateCitation
summary: Validate that cited text appears in source document
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      properties:
        document:
          type: string
          description: Document filename (e.g., "legal-authorities.md")
        page:
          type: integer
          description: Page number (optional)
        section:
          type: string
          description: Section identifier (optional)
        claimed_text:
          type: string
          description: Text that should match the source
```

#### Action 2: Check Feasibility
```yaml
operationId: checkFeasibility
summary: Assess operational feasibility of proposed control
parameters:
  - name: proposed_control
    type: string
    description: Description of the control mechanism
  - name: jurisdiction
    type: string
    description: "el-paso-tx" or "dona-ana-nm"
  - name: utility_type
    type: string
    description: "water", "electric", or "gas"
```

#### Action 3: Search Legal Authority
```yaml
operationId: searchLegalAuthority
summary: Find relevant statutes and regulations
parameters:
  - name: jurisdiction
    type: string
    description: "texas" or "new-mexico"
  - name: topic
    type: string
    description: Search topic (e.g., "utility rates")
  - name: query
    type: string
    description: Specific search query
```

### Step 3: Authentication
- **Type:** None (public API)
- Leave authentication fields empty

### Step 4: Privacy Policy
If required, use:
```
https://celayasolutions.com/privacy
```

---

## 📝 System Prompt

Use this in your CustomGPT instructions:

```markdown
You are Civic Ledger — El Paso Proof Engine, built by Celaya Solutions.

**Core Mission:**
Generate verifiable civic control frameworks that protect El Paso residents from ratepayer cross-subsidy related to data center utility impacts.

**Key Principles:**
- Pro-growth AND pro-fairness
- Evidence-based only (80% documented, 20% inference, 0% speculation)
- No personal attacks — design systems, not accusations
- All outputs must be implementable by existing staff

**Available Actions:**
1. `validateCitation` - Verify text exists in source documents
2. `checkFeasibility` - Assess operational viability of controls
3. `searchLegalAuthority` - Find relevant statutes/regulations

**Output Discipline:**
- Use GREEN confidence when citing exact matches from documents
- Use YELLOW confidence when inferring from related provisions
- Use RED confidence and suggest records requests for missing data
- Always cite sources with document name, page, and quote

**Safety Guardrails:**
- Never provide PII
- Never guide unauthorized system access
- Never make personal accusations
- Always direct to official channels only
- Flag all policy documents for legal counsel review

**Response Format:**
When generating outputs, include:
1. Clear cause → effect analysis
2. Feasibility assessment (validated via action)
3. Source citations (validated via action)
4. Legal review flags where appropriate
```

---

## ✅ Testing Your Setup

### Test 1: Root Health Check
Ask your CustomGPT:
```
Check if the Civic Ledger server is online
```

Expected: Should use the root endpoint and confirm "ok" status

### Test 2: Citation Validation
Ask your CustomGPT:
```
Validate that "Texas Water Code Chapter 13" appears in legal-authorities.md
```

Expected: Should return GREEN confidence with exact match details

### Test 3: Feasibility Check
Ask your CustomGPT:
```
Check if El Paso Water can implement monthly data center water usage reporting
```

Expected: Should assess feasibility based on AMI infrastructure

### Test 4: Full Workflow
Ask your CustomGPT:
```
Generate a staff checklist for implementing a data center water ledger in El Paso
```

Expected: Should combine all actions to produce validated, feasible output

---

## 🚨 Troubleshooting

### Issue: "Failed to connect to action server"
**Solution:**
1. Verify server is running: `curl https://civic-ledger-elpaso.fly.dev/`
2. Check Fly.io status: `flyctl status -a civic-ledger-elpaso`
3. Review logs: `flyctl logs -a civic-ledger-elpaso`

### Issue: "Citation validation returns 500 error"
**Solution:**
1. SSH into container: `flyctl ssh console -a civic-ledger-elpaso`
2. Verify docs exist: `ls /app/docs/`
3. If missing, redeploy with fixed Dockerfile

### Issue: "OpenAPI import fails"
**Solution:**
1. Manually test endpoint: `curl https://civic-ledger-elpaso.fly.dev/openapi.json`
2. Validate JSON: Copy output to https://jsonlint.com/
3. If invalid, check server.py FastAPI route definitions

---

## 📊 Monitoring Deployment

### Real-time Logs
```bash
flyctl logs -a civic-ledger-elpaso
```

### Check Running Instances
```bash
flyctl status -a civic-ledger-elpaso
```

### SSH into Container
```bash
flyctl ssh console -a civic-ledger-elpaso
```

### Force Restart
```bash
flyctl apps restart civic-ledger-elpaso
```

---

## 🎉 Ready to Ship

Once all tests pass:

1. **Document your CustomGPT:**
   - Add description explaining the tool's purpose
   - List example prompts
   - Include safety guidelines

2. **Share with El Paso Community:**
   - Post on social networks with server URL
   - Share example outputs
   - Invite community testing

3. **Push to GitHub:**
   ```bash
   git push origin main
   ```

4. **Monitor for Issues:**
   - Watch Fly.io logs during initial usage
   - Respond to GitHub issues
   - Iterate based on feedback

---

**Need Help?**
- Check logs: `flyctl logs -a civic-ledger-elpaso`
- Review docs: https://fly.io/docs/
- Contact: chris@chriscelaya.com
