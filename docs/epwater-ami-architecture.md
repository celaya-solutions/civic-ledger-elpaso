# EPWater AMI System Architecture

## System Overview

El Paso Water's Advanced Metering Infrastructure (AMI) is a **closed-loop system**:

- **Meter network:** Radio frequency mesh (900 MHz)
- **Data flow:** Meters → Collectors → Utility head-end → MDMS (Meter Data Management System)
- **Internet connectivity:** NOT directly connected to public internet
- **Access control:** Utility personnel only, via secure internal network

## Critical Constraints

❌ **NEVER propose:**
- Direct meter polling from external systems
- Device-level API access
- Public internet exposure of meter data
- Bypassing utility security controls

✅ **ALWAYS design:**
- Data exports FROM utility systems (MDMS → City ledger)
- Batch export protocols (daily/weekly aggregates)
- Authorized personnel execution only
- Data Sharing Agreements between entities

## Reference Architecture
```
[Meters] --RF--> [Collectors] --Backhaul--> [Utility Head-End]
                                                    |
                                                    v
                                            [MDMS Database]
                                                    |
                                        (Authorized Export)
                                                    |
                                                    v
                                        [City/County Ledger] --> [Public Dashboard]
```

## Sources

[GREEN: EPWater public infrastructure documentation, link/date]
[YELLOW: Standard AMI architecture based on industry norms]