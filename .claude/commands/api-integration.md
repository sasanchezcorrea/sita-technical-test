---
description: Guide for integrating real APIs
---

Help the user with API integration based on their question:

1. **If asking about status:**
   - Show which APIs are currently mocked
   - What's needed from external teams
   - Timeline for integration (5 days)

2. **If asking about OptiCore:**
   - Reference `docs/api-integration/REAL-API-INTEGRATION-GUIDE.md`
   - Show what info is needed from OptiCore team
   - Explain code changes required in:
     - `job_processor/app/coordination/opticore_integration.py`
     - `job_processor/app/config.py`
   - Show testing strategy

3. **If asking about Freya:**
   - Reference Freya Climb and Freya Level sections
   - Show what info is needed from Freya team
   - Explain code changes for both services
   - Show testing strategy

4. **If asking about OAuth2:**
   - Explain token refresh implementation
   - Show code changes in `services/external_service_client.py`
   - Provide testing examples

5. **If asking about timeline:**
   - Day 1-2: OptiCore
   - Day 3-4: Freya
   - Day 5: OAuth2 & testing
   - Point to Week 1 plan in `docs/production/PRODUCTION-READINESS-CHECKLIST.md`

Always include:
- Exact file paths to edit
- Code snippets for common changes
- Testing commands
- Validation checklist
