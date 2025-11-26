---
description: Help deploy OptiFlight to an environment
---

Ask the user which environment they want to deploy to:
- **staging** - Auto-deployed via GitLab on merge to main
- **preprod** - Manual deployment for testing
- **production** - Manual deployment (tags only)

Then provide:

1. **Prerequisites** for the chosen environment
2. **Step-by-step deployment commands**
3. **Validation steps** after deployment
4. **Monitoring** what to watch
5. **Rollback procedure** if needed

For **staging:**
- Reference `.gitlab-ci.yml` auto-deployment
- Point to testing checklist

For **preprod:**
- Show how to trigger manual job in GitLab
- Reference `scripts/validate-deployment.sh preprod`

For **production:**
- Show tag creation process
- Reference `docs/production/QUICK-START-PRODUCTION.md`
- Emphasize manual approval step
- Include 4-hour monitoring checklist

Include relevant kubectl/helm commands and GitLab UI navigation.
