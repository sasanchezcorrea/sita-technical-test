---
description: Help debug issues
---

Guide troubleshooting based on the issue:

1. **Ask for Context:**
   - What environment? (local, staging, preprod, prod)
   - What's the error message or symptom?
   - When did it start?
   - What changed recently?

2. **Common Issues & Solutions:**

   **Pipeline Failures:**
   - Lint errors → Run `ruff check` and `ruff format` locally
   - Test failures → Run `pytest` locally with `-v` flag
   - Docker build fails → Check Dockerfile and requirements.txt
   - Deployment fails → Check `kubectl get pods -n <namespace>`

   **API Issues:**
   - Connection timeout → Check circuit breaker status
   - Authentication fails → Verify API keys/OAuth2 tokens
   - Rate limiting → Check request rates, implement backoff
   - Version mismatch → Verify compatibility matrix

   **Database Issues:**
   - Connection fails → Check connection string and credentials
   - Slow queries → Check database logs, add indexes
   - Pool exhausted → Increase pool size in config
   - Migration fails → Rollback and fix, or manual SQL

   **Kubernetes Issues:**
   - Pods not starting → `kubectl describe pod <pod-name>`
   - CrashLoopBackOff → Check logs: `kubectl logs <pod-name>`
   - ImagePullBackOff → Verify image exists in registry
   - OOMKilled → Increase memory limits

3. **Debugging Commands:**
   ```bash
   # Check logs
   kubectl logs -n <namespace> deployment/optiflight-coordinator --tail=100

   # Check pod status
   kubectl get pods -n <namespace>
   kubectl describe pod <pod-name> -n <namespace>

   # Check events
   kubectl get events -n <namespace> --sort-by='.lastTimestamp'

   # Connect to pod
   kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

   # Check database
   psql "$DATABASE_URL" -c "SELECT 1"

   # Check Redis
   redis-cli -u "$REDIS_URL" PING
   ```

4. **Monitoring:**
   - Grafana: Check dashboards
   - Kibana: Search logs
   - Jaeger: Check traces
   - Prometheus: Check alerts

5. **If Still Stuck:**
   - Check relevant documentation in `docs/`
   - Review recent commits: `git log --oneline -10`
   - Check GitLab pipeline logs
   - Contact team on Slack #optiflight-support

Provide step-by-step diagnosis and resolution.
