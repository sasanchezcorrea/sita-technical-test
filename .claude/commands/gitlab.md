---
description: Help with GitLab CI/CD setup and usage
---

Help with GitLab CI/CD based on the user's question:

1. **Initial Setup** (if not done):
   - Guide them to `docs/gitlab/GITLAB-SETUP-CHECKLIST.md`
   - Show the 10-step process
   - Estimated time: 2-3 hours
   - Key steps:
     * Configure protected branches
     * Add CI/CD variables (KUBE_CONFIG_*)
     * Test pipeline

2. **Understanding the Pipeline:**
   - Explain `.gitlab-ci.yml` structure
   - Show 8 stages:
     * lint → test → build → deploy-staging → integration-test → deploy-preprod → deploy-prod → rollback
   - Point to `docs/gitlab/GITLAB-CI-CD-GUIDE.md`

3. **CI/CD Variables:**
   If asking about variables, explain how to add:
   ```
   Settings > CI/CD > Variables

   Required:
   - KUBE_CONFIG_STAGING (Type: File, Masked: Yes)
   - KUBE_CONFIG_PREPROD (Type: File, Protected: Yes, Masked: Yes)
   - KUBE_CONFIG_PROD (Type: File, Protected: Yes, Masked: Yes)
   - SLACK_WEBHOOK (Optional, Type: Variable, Protected: Yes, Masked: Yes)
   ```

   Show how to encode kubeconfig:
   ```bash
   kubectl config view --minify --flatten --context=staging | base64 | tr -d '\n'
   ```

4. **Common Workflows:**

   **Creating a feature:**
   ```bash
   git checkout -b feature/my-feature
   # Make changes
   git push origin feature/my-feature
   # Create MR in GitLab
   # Pipeline runs automatically
   ```

   **Deploying to staging:**
   - Merge MR to main
   - Pipeline auto-deploys to staging
   - Verify at https://optiflight-staging.sita.aero

   **Deploying to production:**
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   # Go to GitLab > Pipelines
   # Find pipeline for tag
   # Click "Play" on deploy:production
   ```

5. **Troubleshooting Pipelines:**
   - Pipeline failing on lint → Run linting locally first
   - Docker build fails → Test build locally
   - Deployment fails → Check kubeconfig, namespace, secrets
   - Integration tests fail → Check staging is actually deployed

6. **Best Practices:**
   - Protect main branch
   - Require approvals for MRs
   - Use conventional commits
   - Tag production releases (v*.*.*)
   - Monitor pipeline status

Always include links to relevant docs and command examples.
