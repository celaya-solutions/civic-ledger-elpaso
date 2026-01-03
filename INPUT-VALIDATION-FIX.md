# 🔧 Input Validation Fix Guide

## The Problem

CustomGPT is sending reasonable requests like:
```json
{
  "control_type": "data_center_water_disclosure",
  "scope": "citywide",
  "jurisdiction": "city_of_elpaso"
}
```

But your API expects exact enum values:
```json
{
  "control_type": "cost_of_service_study",  // only 3 options
  "scope": "all_data_centers",              // only 3 options  
  "jurisdiction": "elpaso"                   // exact match
}
```

---

## ✅ RECOMMENDED SOLUTION

**Update the CustomGPT instructions** to include valid parameter values.

Add this section to `system-prompt-optimal.md`:

```markdown
## API PARAMETER REFERENCE

When using the cost_benefit_calculator tool:

**control_type** (choose one):
- `cost_of_service_study` - For rate analysis and cost allocation
- `dashboard_development` - For public transparency portals
- `independent_audit` - For third-party verification

**scope** (choose one):
- `single_facility` - Individual data center
- `all_data_centers` - Aggregate across all facilities
- `system_wide` - Entire utility system impact

**jurisdiction**:
- Must be exactly: `elpaso`

**Example:**
```json
{
  "control_type": "cost_of_service_study",
  "scope": "all_data_centers",
  "jurisdiction": "elpaso"
}
```
```

---

## Alternative: Server-Side Mapping

If you want the server to be more flexible, update the Pydantic model with validators:

```python
from pydantic import field_validator

class CostBenefitInput(BaseModel):
    control_type: str
    scope: str
    jurisdiction: str
    
    @field_validator('control_type')
    @classmethod
    def normalize_control_type(cls, v: str) -> str:
        """Map flexible input to valid types"""
        v_lower = v.lower().replace('_', ' ')
        
        # Map common variations
        if 'cost' in v_lower or 'study' in v_lower:
            return 'cost_of_service_study'
        elif 'dashboard' in v_lower or 'portal' in v_lower:
            return 'dashboard_development'
        elif 'audit' in v_lower:
            return 'independent_audit'
            
        # If exact match, return it
        valid = ['cost_of_service_study', 'dashboard_development', 'independent_audit']
        if v in valid:
            return v
            
        raise ValueError(f"control_type must be one of: {', '.join(valid)}")
    
    @field_validator('scope')
    @classmethod
    def normalize_scope(cls, v: str) -> str:
        """Map flexible input to valid scopes"""
        v_lower = v.lower()
        
        # Map variations
        if 'single' in v_lower or 'one' in v_lower or 'facility' in v_lower:
            return 'single_facility'
        elif 'all' in v_lower or 'data center' in v_lower:
            return 'all_data_centers'
        elif 'system' in v_lower or 'wide' in v_lower or 'city' in v_lower:
            return 'system_wide'
            
        # If exact match, return it
        valid = ['single_facility', 'all_data_centers', 'system_wide']
        if v in valid:
            return v
            
        raise ValueError(f"scope must be one of: {', '.join(valid)}")
    
    @field_validator('jurisdiction')
    @classmethod
    def normalize_jurisdiction(cls, v: str) -> str:
        """Normalize jurisdiction input"""
        v_lower = v.lower().replace('_', ' ')
        
        if 'el paso' in v_lower or 'elpaso' in v_lower:
            return 'elpaso'
        if v == 'elpaso':
            return v
            
        raise ValueError("jurisdiction must be 'elpaso'")
```

---

## 🎯 QUICK FIX (Recommended)

**Update your CustomGPT instructions right now:**

1. Open your CustomGPT
2. Edit instructions
3. Add the "API Parameter Reference" section above
4. Save

This teaches CustomGPT the exact values to use.

---

## 📊 All Valid Parameters

### cost_benefit_calculator
```
control_type: 
  - cost_of_service_study
  - dashboard_development
  - independent_audit

scope:
  - single_facility
  - all_data_centers
  - system_wide

jurisdiction:
  - elpaso
```

### check_feasibility
```
jurisdiction:
  - elpaso
  - santa_teresa

utility_type:
  - water
  - electric
  - gas
```

### search_legal_authority
```
jurisdiction:
  - texas
  - new_mexico

topic:
  - development_agreements
  - utility_regulation
  - open_records
```

### load_comparable_precedent
```
jurisdiction:
  - loudoun_county
  - mesa
  - raleigh_durham

document_type:
  - development_agreement
  - water_contract
  - rate_structure

topic:
  - infrastructure_escrow
  - cost_allocation
  - transparency
```

### generate_records_request
```
jurisdiction:
  - city_of_elpaso
  - epwater
  - dona_ana_county

document_type:
  - board_minutes
  - development_agreement
  - cost_study
```

---

## ✅ ACTION ITEMS

**Option 1: Quick Fix (5 min)**
- Update CustomGPT instructions with valid parameters
- Test again

**Option 2: Flexible Server (30 min)**
- Add field validators to server.py
- Redeploy to Fly.io
- Test with CustomGPT

**Recommendation:** Start with Option 1, add Option 2 later if needed.
