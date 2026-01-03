# System Prompt Selection Guide

## 📊 COMPARISON

| Feature | system-prompt.md | system-prompt-gpt.md | **system-prompt-optimal.md** |
|---------|------------------|----------------------|------------------------------|
| **Length** | ~2,200 words | ~300 words | ~1,100 words |
| **Legal disclaimers** | ✅ Extensive | ❌ Missing | ✅ Comprehensive |
| **Safety boundaries** | ✅ 5 detailed | ✅ Basic | ✅ 5 detailed |
| **EPWater AMI constraints** | ✅ Detailed | ❌ Missing | ✅ Included |
| **Tool integration** | ❌ Not mentioned | ✅ Lists all 9 | ✅ Lists all 9 |
| **Evidence discipline** | ✅ GREEN/YELLOW/RED | ✅ GREEN/YELLOW/RED | ✅ GREEN/YELLOW/RED |
| **Output format** | ✅ Structured | ❌ Minimal | ✅ Structured |
| **Error examples** | ✅ Included | ❌ Missing | ✅ Included |
| **CustomGPT token fit** | ⚠️ May exceed | ✅ Fits easily | ✅ Fits comfortably |

---

## ✅ RECOMMENDATION

**Use: `system-prompt-optimal.md`**

This hybrid version:
- ✅ Includes all critical safety boundaries
- ✅ References all 9 API actions
- ✅ Has legal disclaimers and EPWater constraints
- ✅ Fits within CustomGPT limits (~1,100 words)
- ✅ Maintains professional tone
- ✅ Includes error handling examples

---

## 🎯 FOR CUSTOMGPT CONFIGURATION

**Copy this into CustomGPT "Instructions" field:**

```
[Paste entire contents of system-prompt-optimal.md]
```

**Why this version:**
1. **Safety first** - All 5 hard boundaries clearly stated
2. **Tool integration** - Explicitly tells CustomGPT to use the 9 actions
3. **Legal protection** - Comprehensive disclaimers
4. **EPWater security** - Critical AMI constraints included
5. **Actionable** - Clear output format and workflow

---

## 📝 WHAT EACH VERSION IS GOOD FOR

### system-prompt.md (The Original)
**Best for:** Internal documentation, training materials, comprehensive reference

**Use when:**
- Onboarding new team members
- Creating detailed documentation
- Need complete procedural guide

**Don't use for:** CustomGPT (too long)

---

### system-prompt-gpt.md (The Minimal)
**Best for:** Quick testing, minimal viable product

**Use when:**
- Rapid prototyping
- Simple use cases
- Token budget is critical

**Don't use for:** Production deployment (missing safety boundaries)

---

### system-prompt-optimal.md (The Hybrid) ⭐
**Best for:** Production CustomGPT deployment

**Use when:**
- Deploying to public
- Need comprehensive safety
- Want tool integration
- Require legal disclaimers

**This is your production version.** ✅

---

## 🚀 DEPLOY IT NOW

1. Open https://chat.openai.com/
2. Go to "My GPTs" → Create
3. Name: "Civic Ledger — El Paso Proof Engine"
4. Click "Configure"
5. In "Instructions", paste **entire contents** of `system-prompt-optimal.md`
6. Add actions from: `https://civic-ledger-elpaso.fly.dev/openapi.json`
7. Save and test!

---

## ✅ SAFETY VERIFICATION

The optimal prompt includes:

**Hard Boundaries:**
- ✅ No PII
- ✅ No unauthorized access
- ✅ No personal accusations
- ✅ No harassment
- ✅ No legal powers without authority

**Technical Constraints:**
- ✅ EPWater AMI security (closed-loop)
- ✅ Authorized data exports only
- ✅ No direct meter access

**Legal Protection:**
- ✅ "Not legal advice" disclaimer
- ✅ Requires counsel review for policy docs
- ✅ Verification checklist required

**Tone Control:**
- ✅ Pro-growth AND pro-fairness
- ✅ No personal attacks
- ✅ Official channels only

---

**VERDICT: Use `system-prompt-optimal.md` for your CustomGPT! 🎯**
