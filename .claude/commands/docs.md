---
description: Navigate and find documentation
---

Help the user find relevant documentation based on their question:

**Quick Navigation:**

📁 **Production Deployment:**
- Start: `docs/production/PRODUCTION-DEPLOYMENT-SUMMARY.md` ⭐
- Checklist: `docs/production/PRODUCTION-READINESS-CHECKLIST.md`
- Secrets: `docs/production/PRODUCTION-SECRETS-TEMPLATE.md`
- Quick ref: `docs/production/QUICK-START-PRODUCTION.md`

📁 **GitLab CI/CD:**
- Start: `docs/gitlab/GITLAB-PRODUCTION-READY.md` ⭐
- Setup: `docs/gitlab/GITLAB-SETUP-CHECKLIST.md`
- Usage: `docs/gitlab/GITLAB-CI-CD-GUIDE.md`

📁 **API Integration:**
- Guide: `docs/api-integration/REAL-API-INTEGRATION-GUIDE.md`

📁 **Architecture & Guides:**
- Architecture: `docs/guides/ARCHITECTURE-FLOW-GUIDE.md`
- Deployment: `docs/guides/DEPLOYMENT-GUIDE.md`
- Testing: `docs/guides/INTEGRATION-TEST-REPORT.md`

📁 **Project Status:**
- Next steps: `NEXT-STEPS.md`
- Missing items: `MISSING-ITEMS.md`
- Gap analysis: `COMPREHENSIVE-GAP-ANALYSIS.md`

**Documentation Index:**

If user asks "what documentation exists?", provide a structured list:

```
OptiFlight Documentation
├── Production Deployment (docs/production/)
│   ├── PRODUCTION-DEPLOYMENT-SUMMARY.md - Executive summary
│   ├── PRODUCTION-READINESS-CHECKLIST.md - Day-by-day plan
│   ├── PRODUCTION-SECRETS-TEMPLATE.md - All secrets needed
│   └── QUICK-START-PRODUCTION.md - Quick commands
├── GitLab CI/CD (docs/gitlab/)
│   ├── GITLAB-PRODUCTION-READY.md - Overview
│   ├── GITLAB-SETUP-CHECKLIST.md - 10-step setup
│   └── GITLAB-CI-CD-GUIDE.md - Usage guide
├── API Integration (docs/api-integration/)
│   └── REAL-API-INTEGRATION-GUIDE.md - Connect real APIs
├── Architecture (docs/guides/)
│   ├── ARCHITECTURE-FLOW-GUIDE.md - System design
│   ├── DEPLOYMENT-GUIDE.md - General deployment
│   └── INTEGRATION-TEST-REPORT.md - Test results
└── Project Status (root/)
    ├── NEXT-STEPS.md - What's next (94% complete!)
    ├── MISSING-ITEMS.md - What's remaining
    └── COMPREHENSIVE-GAP-ANALYSIS.md - Detailed analysis
```

**Search by Topic:**

If user asks about specific topics, provide relevant docs:
- **Deployment** → `docs/production/`
- **GitLab** → `docs/gitlab/`
- **APIs** → `docs/api-integration/`
- **Testing** → `docs/guides/INTEGRATION-TEST-REPORT.md`
- **Architecture** → `docs/guides/ARCHITECTURE-FLOW-GUIDE.md`
- **Status** → `NEXT-STEPS.md`

Always provide the full path and a brief description of what the doc contains.
