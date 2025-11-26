# Phase 1: Deployment with Mock Services - Quick Start Guide

**Status:** Ready to Deploy
**Duration:** 1-2 weeks
**Objective:** Validate deployment infrastructure and processes with mock external services

---

## 📋 Prerequisites

Before starting Phase 1 deployment, ensure you have:

- [ ] On-premises Kubernetes cluster (1.27+) with 5+ nodes
- [ ] kubectl configured and connected to cluster
- [ ] Helm 3.x installed
- [ ] Container registry access (registry.sita.aero)
- [ ] GitLab CI/CD access with appropriate permissions

---

## 🚀 Quick Start (5 Steps)

### Step 1: Set Up Container Registry

Configure GitLab CI/CD variables for container registry:

```bash
# In GitLab: Settings > CI/CD > Variables
CI_REGISTRY_USER=<your-registry-username>
CI_REGISTRY_PASSWORD=<your-registry-password>
CI_REGISTRY=registry.sita.aero
```

### Step 2: Install Sealed Secrets Controller

```bash
# Install sealed-secrets for secure secret management
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Verify installation
kubectl get pods -n kube-system | grep sealed-secrets
```

### Step 3: Create Namespaces

```bash
# Create all environment namespaces
kubectl apply -f k8s/namespaces/environments.yaml

# Verify namespaces
kubectl get namespaces | grep optiflight
```

**Expected output:**
```
optiflight-staging   Active   1m
optiflight-preprod   Active   1m
optiflight-prod      Active   1m
```

### Step 4: Create Sealed Secrets

Generate secure passwords and create sealed secrets for each environment:

```bash
# Generate secure passwords
STAGING_DB_PASS=$(openssl rand -base64 32)
STAGING_REDIS_PASS=$(openssl rand -base64 32)
STAGING_KAFKA_PASS=$(openssl rand -base64 32)
STAGING_RABBITMQ_PASS=$(openssl rand -base64 32)

# Create sealed secrets for staging
./scripts/create-sealed-secret.sh staging database \
  "POSTGRES_PASSWORD=${STAGING_DB_PASS}" \
  "DATABASE_URL=postgresql://optiflight:${STAGING_DB_PASS}@postgresql:5432/optiflight_staging"

./scripts/create-sealed-secret.sh staging redis \
  "REDIS_PASSWORD=${STAGING_REDIS_PASS}"

./scripts/create-sealed-secret.sh staging kafka \
  "KAFKA_PASSWORD=${STAGING_KAFKA_PASS}"

./scripts/create-sealed-secret.sh staging rabbitmq \
  "RABBITMQ_PASSWORD=${STAGING_RABBITMQ_PASS}"

# Apply sealed secrets
kubectl apply -f k8s/sealed-secrets/staging-*.yaml
```

**Repeat for preprod and production** with different passwords.

### Step 5: Install KEDA

```bash
# Install KEDA for event-driven autoscaling
./scripts/install_keda.sh

# Verify KEDA installation
kubectl get pods -n keda
```

**Expected output:**
```
NAME                                      READY   STATUS    RESTARTS   AGE
keda-operator-<hash>                      1/1     Running   0          1m
keda-operator-metrics-apiserver-<hash>    1/1     Running   0          1m
```

---

## 🏗️ Deployment Process

### Option A: GitLab CI/CD (Recommended)

**Automatic deployment via GitLab pipeline:**

```bash
# 1. Commit all changes
git add .
git commit -m "feat: Phase 1 deployment configuration with mock services"
git push origin main

# 2. Create release candidate tag
git tag -a v1.0.0-rc1 -m "Release Candidate 1 - Mock Services"
git push origin v1.0.0-rc1
```

**GitLab will automatically:**
- ✅ Run linting (ruff, mypy, bandit)
- ✅ Run tests with coverage
- ✅ Build main application Docker image
- ✅ Build mock service Docker images (OptiCore, Freya Climb, Freya Level)
- ✅ Run security scans (Trivy)
- ✅ Deploy to staging automatically

**Monitor pipeline:**
- Go to GitLab → CI/CD → Pipelines
- Watch the pipeline execution
- All stages should pass ✅

### Option B: Manual Deployment

If you prefer manual control:

```bash
# Deploy to staging
./scripts/deploy-staging.sh v1.0.0-rc1

# Validate staging deployment
./scripts/validate-deployment.sh staging
```

---

## ✅ Validation Steps

### Check Staging Deployment

```bash
# 1. Check all pods are running
kubectl get pods -n optiflight-staging

# Expected pods:
# - optiflight-coordinator-xxx (1 replica)
# - mock-opticore-xxx (1 replica)
# - mock-freya-climb-xxx (1 replica)
# - mock-freya-level-xxx (1 replica)
# - postgresql-0
# - redis-master-0
# - kafka-0
# - rabbitmq-0

# 2. Run comprehensive validation (25 checks)
./scripts/validate-deployment.sh staging

# Expected result: 25/25 tests passing ✅

# 3. Check services
kubectl get svc -n optiflight-staging

# 4. Check ingress
kubectl get ingress -n optiflight-staging
```

### Test Application Endpoints

```bash
# Port forward to staging
kubectl port-forward -n optiflight-staging svc/optiflight-coordinator 8000:80

# Test health endpoint
curl http://localhost:8000/health

# Test metrics endpoint
curl http://localhost:8000/metrics

# Test API endpoint
curl http://localhost:8000/api/v1/coordination/version
```

**Expected responses:**
- Health: `{"status": "healthy"}`
- Metrics: Prometheus metrics output
- Version: Version information with external service status

### Run Integration Tests

```bash
cd job_processor

# Run integration tests against staging
pytest tests/test_integration.py -v \
  --api-url=http://optiflight-staging.sita.aero

# Test complete workflow
./demo-realistic-workflow.sh

# Load testing
python load_test.py \
  --url http://optiflight-staging.sita.aero \
  --requests 1000 \
  --concurrent 10
```

---

## 📈 Promote to Pre-Production

Once staging validation is complete:

### Via GitLab (Recommended)

```bash
# In GitLab UI:
# 1. Go to CI/CD → Pipelines
# 2. Find pipeline for v1.0.0-rc1
# 3. Click "Deploy to Pre-prod" (manual action)
# 4. Confirm deployment
```

### Manual Promotion

```bash
./scripts/deploy-preprod.sh v1.0.0-rc1

# Validate preprod
./scripts/validate-deployment.sh preprod
```

---

## 🎯 Deploy to Production

After successful preprod validation:

### Create Production Tag

```bash
# Create production release tag
git tag -a v1.0.0 -m "Production Release - Phase 1 Mock Services"
git push origin v1.0.0
```

### Deploy via GitLab

```bash
# In GitLab UI:
# 1. Pipeline runs automatically for tag
# 2. Manual approval required for production
# 3. Click "Deploy to Production"
# 4. Confirm deployment
```

### Validate Production

```bash
./scripts/validate-deployment.sh production

# Additional production checks
kubectl get pods -n optiflight-prod
kubectl top pods -n optiflight-prod
kubectl get hpa -n optiflight-prod  # Check autoscaling
```

---

## 🔍 Observability

### Check ELK Stack

```bash
# Check Elasticsearch
kubectl get pods -n monitoring | grep elasticsearch

# Access Kibana
# URL: https://kibana.sita.aero
# Import dashboards from: helm/dashboards/

# Verify log ingestion
kubectl logs -n optiflight-prod deployment/optiflight-coordinator --tail=100
```

### Check Grafana

```bash
# Check Grafana pods
kubectl get pods -n monitoring | grep grafana

# Access Grafana
# URL: https://grafana.sita.aero

# Import dashboards:
# - OptiFlight Overview
# - OptiFlight Performance
# - External APIs (for Phase 2)
```

### Check Prometheus Alerts

```bash
# Check Prometheus
kubectl get pods -n monitoring | grep prometheus

# View active alerts
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Open: http://localhost:9090/alerts
```

---

## 🧪 Testing Scenarios

### Scenario 1: Basic Flight Optimization

```bash
curl -X POST http://optiflight-staging.sita.aero/api/v1/events/position \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": "ABC123",
    "airline": "TEST",
    "latitude": 41.405937,
    "longitude": 2.178605,
    "altitude": 35000,
    "timestamp": "2025-11-25T10:00:00Z"
  }'
```

### Scenario 2: Load Testing

```bash
# 1000 requests with 10 concurrent connections
cd job_processor
python load_test.py \
  --url http://optiflight-staging.sita.aero \
  --requests 1000 \
  --concurrent 10 \
  --output load_test_results.json

# Check results
cat load_test_results.json | jq '.summary'
```

### Scenario 3: Auto-Scaling Test

```bash
# Generate load to trigger autoscaling
./scripts/test_autoscaling.sh optiflight-staging

# Watch pods scale
watch kubectl get pods -n optiflight-staging
```

**Expected:** Pods should scale from 1 → 5 based on load.

---

## 🐛 Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n optiflight-staging

# Describe pod
kubectl describe pod <pod-name> -n optiflight-staging

# Check logs
kubectl logs <pod-name> -n optiflight-staging

# Common issues:
# - ImagePullBackOff: Check registry credentials
# - CrashLoopBackOff: Check application logs
# - Pending: Check resource quotas
```

### Mock Services Not Responding

```bash
# Check mock service pods
kubectl get pods -n optiflight-staging | grep mock

# Check mock service logs
kubectl logs -n optiflight-staging deployment/mock-opticore
kubectl logs -n optiflight-staging deployment/mock-freya-climb
kubectl logs -n optiflight-staging deployment/mock-freya-level

# Test mock service directly
kubectl port-forward -n optiflight-staging svc/mock-opticore 8001:8001
curl http://localhost:8001/health
```

### Database Connection Issues

```bash
# Check PostgreSQL pod
kubectl get pods -n optiflight-staging | grep postgresql

# Connect to PostgreSQL
kubectl exec -it -n optiflight-staging postgresql-0 -- psql -U optiflight -d optiflight_staging

# Test connection from app
kubectl exec -it -n optiflight-staging deployment/optiflight-coordinator -- \
  python -c "from app.database import engine; print(engine.connect())"
```

### KEDA Not Autoscaling

```bash
# Check KEDA operator
kubectl get pods -n keda

# Check ScaledObjects
kubectl get scaledobjects -n optiflight-staging

# Describe ScaledObject
kubectl describe scaledobject optiflight-coordinator-kafka -n optiflight-staging

# Check HPA created by KEDA
kubectl get hpa -n optiflight-staging
```

---

## 📊 Success Criteria for Phase 1

- [ ] All 3 environments deployed (staging, preprod, production)
- [ ] GitLab CI/CD pipeline executing end-to-end
- [ ] All mock services responding correctly
- [ ] Integration tests passing (100% success rate)
- [ ] Observability stack collecting metrics and logs
- [ ] Auto-scaling working (KEDA responding to queue depth)
- [ ] Network policies enforcing isolation
- [ ] Rollback procedure tested
- [ ] Load test: 1000 req/s handled successfully
- [ ] Documentation complete and accessible

---

## 🔄 Rollback Procedure

If issues occur during deployment:

```bash
# Rollback to previous version
./scripts/rollback.sh <environment>

# For staging
./scripts/rollback.sh staging

# Verify rollback
./scripts/validate-deployment.sh staging
```

**Rollback time:** < 5 minutes

---

## 📚 Key Files Modified in Phase 1

- ✅ `job_processor/app/config.py` - Added external service configuration
- ✅ `helm/values-staging.yaml` - Mock service configuration
- ✅ `helm/values-preprod.yaml` - Mock service configuration
- ✅ `helm/values-prod.yaml` - Mock service configuration
- ✅ `helm/templates/mock-services-deployment.yaml` - Mock service Helm template (NEW)
- ✅ `.gitlab-ci.yml` - Added mock service builds
- ✅ `k8s/namespaces/environments.yaml` - Pod security standards

---

## 🎯 Next Steps: Phase 2

Once Phase 1 is stable and validated:

1. **Request API credentials** from external teams:
   - OptiCore team
   - Freya team

2. **Prepare for real API integration:**
   - Create service factory pattern
   - Update configuration for real endpoints
   - Implement API connectivity tests

3. **Plan gradual rollout:**
   - Canary deployment in preprod (20% → 50% → 100%)
   - Blue-green deployment to production

**See:** `/Users/santiagosanchezcorrea/.claude/plans/golden-roaming-whale.md` for complete Phase 2 plan.

---

## 💡 Tips for Success

1. **Monitor continuously:** Keep GitLab pipeline dashboard open during deployment
2. **Validate at each step:** Don't proceed until current environment is stable
3. **Save credentials securely:** Store all generated passwords in a password manager
4. **Document issues:** Create GitLab issues for any problems encountered
5. **Team communication:** Keep team updated via Slack/email on deployment progress

---

## 📞 Support

**If you encounter issues:**
- Check this troubleshooting section first
- Review GitLab pipeline logs
- Use Claude: `/troubleshoot` for systematic debugging
- Escalate to DevOps team if needed

---

**Last Updated:** 2025-11-25
**Phase:** 1 of 3
**Status:** ✅ Ready for Deployment

**Good luck with Phase 1! 🚀**
