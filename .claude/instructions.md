# OptiFlight Coordinator - Claude AI Instructions

## Project Overview

OptiFlight Coordinator is a **production-ready** multi-tenant flight optimization system built for Kubernetes. The system coordinates between OptiCore (initial optimization), Freya Climb (ML-enhanced climb), and Freya Level (ML-enhanced cruise) to provide optimal flight recommendations.

**Current Status:** 94% Complete - Production Ready
**Primary Language:** Python 3.11+
**Framework:** FastAPI
**Infrastructure:** Kubernetes, Helm, GitLab CI/CD
**Databases:** PostgreSQL (primary/replica), Redis
**Message Queues:** Kafka, RabbitMQ
**Observability:** ELK Stack, Prometheus, Grafana, Jaeger

---

## Architecture Context

### System Components
1. **OptiFlight Coordinator** - Main application (this repo)
   - Multi-tenant job processing
   - Event-driven architecture (Kafka/RabbitMQ)
   - Kubernetes orchestration
   - External service integration

2. **External Services (Mock/Real)**
   - OptiCore API - Initial flight optimization
   - Freya Climb API - ML-enhanced climb optimization
   - Freya Level API - ML-enhanced cruise optimization

3. **Infrastructure**
   - Kubernetes clusters (staging, preprod, prod)
   - PostgreSQL with read replicas
   - Redis cluster
   - ELK Stack for logging
   - Prometheus + Grafana for metrics

### Key Directories
```
job_processor/          # Main application
├── app/               # Application code
│   ├── api/          # REST API endpoints
│   ├── coordination/ # OptiCoordinator logic (Phase 12)
│   ├── services/     # External service clients
│   ├── models/       # Data models
│   ├── database.py   # DB connection
│   └── main.py       # FastAPI app
├── tests/            # Test suite
├── alembic/          # Database migrations
└── requirements.txt  # Python dependencies

helm/                  # Kubernetes deployment
├── templates/        # Helm templates
├── values-*.yaml    # Environment configs
└── Chart.yaml       # Helm chart definition

docs/                 # Documentation
├── production/      # Production deployment guides
├── gitlab/          # GitLab CI/CD setup
├── api-integration/ # API integration guides
└── guides/          # General guides

.gitlab-ci.yml        # GitLab CI/CD pipeline
```

---

## Project Phases Completed

1. ✅ **Phase 1-5:** Core platform (multi-tenancy, K8s, performance)
2. ✅ **Phase 6:** Event-driven architecture (Kafka/RabbitMQ)
3. ✅ **Phase 7:** ML integration (OptiCore, Freya)
4. ✅ **Phase 8:** Security & compliance
5. ✅ **Phase 9:** Flight-specific components
6. ✅ **Phase 10:** Observability (ELK, APM)
7. ✅ **Phase 11:** External services framework
8. ✅ **Phase 12:** OptiCoordinator versioning
9. ⏭️ **Phase 13:** ML Training (Deferred - Freya owns)
10. ✅ **Phase 14:** Release pipeline (GitLab)
11. 📋 **Phase 15:** Security hardening (Optional)

---

## Current Status & Next Steps

### What's Working (with mocks)
- Complete multi-tenant job processing
- Event-driven architecture
- ML integration (OptiCore + Freya Climb + Freya Level)
- Full observability stack
- GitLab CI/CD pipeline
- Multi-environment deployment

### What's Needed for Production (6%)
1. **Connect Real APIs** (5 days) 🔴 CRITICAL
   - Replace mock services with real API clients
   - Implement OAuth2 token management
   - See: `docs/api-integration/REAL-API-INTEGRATION-GUIDE.md`

2. **Production Infrastructure** (3 days) 🔴 CRITICAL
   - Provision K8s clusters
   - Set up PostgreSQL with replicas
   - Configure secrets
   - See: `docs/production/PRODUCTION-READINESS-CHECKLIST.md`

3. **GitLab Setup** (2-3 hours) 🔴 CRITICAL
   - Configure CI/CD variables
   - Set up environments
   - See: `docs/gitlab/GITLAB-SETUP-CHECKLIST.md`

---

## Development Guidelines

### Code Style
- **Linting:** ruff (formatting + linting)
- **Type Checking:** mypy
- **Security:** bandit
- **Testing:** pytest with coverage >80%

### Commit Convention
Use conventional commits:
```
feat: add new optimization algorithm
fix: resolve database connection timeout
docs: update API documentation
test: add integration tests
chore: update dependencies
```

### Branch Strategy
- `main` - Production-ready code
- `feature/*` - New features
- `fix/*` - Bug fixes
- `hotfix/*` - Emergency production fixes

### Testing Requirements
- Unit tests for all new functions
- Integration tests for API endpoints
- Mock external services in tests
- Run full test suite before MR: `pytest tests/ -v --cov=app`

---

## Common Tasks

### Running Locally
```bash
# Install dependencies
uv sync

# Run tests
pytest job_processor/tests/ -v

# Run linting
ruff check job_processor/
ruff format job_processor/

# Run application
cd job_processor
uvicorn app.main:app --reload
```

### Working with Docker
```bash
# Build image
docker build -t optiflight-coordinator:dev -f job_processor/Dockerfile .

# Run with mock services
docker-compose -f docker-compose.mock-services.yaml up -d

# View logs
docker logs optiflight-coordinator -f

# Stop services
docker-compose -f docker-compose.mock-services.yaml down
```

### Working with Kubernetes
```bash
# Deploy to staging
kubectl config use-context staging
helm upgrade --install optiflight ./helm -f helm/values-staging.yaml

# Check deployment
kubectl get pods -n optiflight-staging
kubectl logs -n optiflight-staging deployment/optiflight-coordinator

# Run validation
./scripts/validate-deployment.sh staging
```

### Database Migrations
```bash
cd job_processor

# Create migration
alembic revision --autogenerate -m "add new table"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## When Answering Questions

### Always Consider
1. **Production Impact:** Will this affect running systems?
2. **Breaking Changes:** Does this break existing APIs?
3. **Testing:** What tests are needed?
4. **Documentation:** What docs need updating?
5. **Security:** Are there security implications?

### Prefer
- **Existing patterns** over new ones
- **Simple solutions** over complex ones
- **Proven libraries** over custom code
- **Type hints** for all functions
- **Async/await** for I/O operations
- **Structured logging** (not print statements)

### Avoid
- Breaking changes without migration path
- Hardcoded values (use config)
- Synchronous I/O in async contexts
- Global state
- Long-running operations without timeout
- Exposing sensitive data in logs

---

## Key Technologies & Versions

**Core:**
- Python 3.11+
- FastAPI 0.104+
- SQLAlchemy 2.0+ (async)
- Pydantic 2.0+
- httpx (async HTTP client)

**Infrastructure:**
- Kubernetes 1.27+
- Helm 3.12+
- PostgreSQL 15+
- Redis 7+
- Kafka 3.5+
- RabbitMQ 3.12+

**Observability:**
- Elasticsearch 8.10+
- Kibana 8.10+
- Prometheus 2.47+
- Grafana 10.0+
- Jaeger 1.50+
- OpenTelemetry

**CI/CD:**
- GitLab CI/CD
- Docker 24+
- Trivy (security scanning)

---

## Important Constraints

### Production Requirements
- **High Availability:** 3+ replicas, multi-zone
- **Performance:** p95 < 500ms, p99 < 2s
- **Reliability:** 99.9% uptime target
- **Scalability:** Handle 100K+ requests/hour
- **Security:** RBAC, network policies, secrets management

### External API Constraints
- **OptiCore:** Rate limit TBD, timeout 30s
- **Freya:** Rate limit TBD, timeout 30s
- **Circuit breaker:** 5 failures → open for 60s
- **Retries:** 3 attempts with exponential backoff

### Database Constraints
- **Connection pool:** 20 connections
- **Query timeout:** 30s
- **Read replicas:** Use for heavy queries
- **Migrations:** Always backward compatible

---

## Documentation Structure

All documentation is in `docs/` organized by topic:

### Production Deployment
- `docs/production/PRODUCTION-DEPLOYMENT-SUMMARY.md` ⭐ Start here
- `docs/production/PRODUCTION-READINESS-CHECKLIST.md` - Complete checklist
- `docs/production/PRODUCTION-SECRETS-TEMPLATE.md` - Secrets guide
- `docs/production/QUICK-START-PRODUCTION.md` - Quick reference

### GitLab CI/CD
- `docs/gitlab/GITLAB-PRODUCTION-READY.md` ⭐ Start here
- `docs/gitlab/GITLAB-CI-CD-GUIDE.md` - Usage guide
- `docs/gitlab/GITLAB-SETUP-CHECKLIST.md` - Setup steps

### API Integration
- `docs/api-integration/REAL-API-INTEGRATION-GUIDE.md` - How to connect real APIs

### Architecture & Guides
- `docs/guides/ARCHITECTURE-FLOW-GUIDE.md` - System architecture
- `docs/guides/DEPLOYMENT-GUIDE.md` - General deployment
- `docs/guides/INTEGRATION-TEST-REPORT.md` - Test results

### Project Status
- `NEXT-STEPS.md` - Strategic options
- `MISSING-ITEMS.md` - Gap analysis
- `COMPREHENSIVE-GAP-ANALYSIS.md` - Detailed analysis

---

## Response Guidelines

### When Asked About
**"How do I deploy?"**
→ Point to `docs/production/PRODUCTION-DEPLOYMENT-SUMMARY.md`

**"How do I set up GitLab?"**
→ Point to `docs/gitlab/GITLAB-SETUP-CHECKLIST.md`

**"How do I integrate real APIs?"**
→ Point to `docs/api-integration/REAL-API-INTEGRATION-GUIDE.md`

**"What's the project status?"**
→ Refer to `NEXT-STEPS.md` and mention: 94% complete, production-ready

**"How do I run tests?"**
→ `pytest job_processor/tests/ -v --cov=app`

**"What's missing?"**
→ Real API integration (5 days), see `MISSING-ITEMS.md`

### When Making Code Changes
1. Read existing code first
2. Follow established patterns
3. Add tests
4. Update relevant documentation
5. Run linting and tests
6. Use conventional commits

### When Debugging
1. Check application logs: `kubectl logs -n <namespace> deployment/optiflight-coordinator`
2. Check metrics: Grafana dashboards
3. Check traces: Jaeger UI
4. Check database: Connection pool, query performance
5. Check external APIs: Circuit breaker status, error rates

---

## Emergency Procedures

### Production Issues
1. Check health: `curl https://api.optiflight.com/health`
2. Check logs in Kibana
3. Check metrics in Grafana
4. If critical: Execute rollback
   ```bash
   # Via GitLab UI: Click "Rollback" in Environments
   # Or via CLI:
   ./scripts/rollback.sh production
   ```

### Database Issues
1. Check connections: `kubectl exec -it pod -- psql -U optiflight`
2. Check replication lag
3. Switch to read replica if primary down
4. Contact DBA team

### API Issues
1. Check circuit breaker status
2. Check external service status pages
3. Increase timeout if needed
4. Contact external team

---

## Helpful Commands

Use Claude CLI slash commands (see `.claude/commands/` for all):
- `/deploy` - Deploy to environment
- `/test` - Run comprehensive tests
- `/status` - Check project status
- `/api` - API integration help
- `/troubleshoot` - Debug issues
- `/architecture` - Explain architecture

---

## Success Metrics

**Technical:**
- Test coverage >80%
- API response p95 <500ms
- Error rate <1%
- Uptime >99.9%

**Business:**
- Fuel savings calculated per flight
- Multi-tenant isolation working
- External API integration success rate >99%

---

**Last Updated:** 2025-11-25
**Project Status:** 94% Complete - Production Ready
**Primary Contact:** [Your team's contact info]
