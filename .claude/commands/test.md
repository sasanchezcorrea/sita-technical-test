---
description: Run comprehensive tests
---

Guide the user through running tests for OptiFlight:

1. **Quick Checks** (30 seconds)
   ```bash
   # Linting
   ruff check job_processor/
   ruff format --check job_processor/

   # Type checking
   mypy job_processor/app --ignore-missing-imports
   ```

2. **Unit Tests** (3-5 minutes)
   ```bash
   cd job_processor
   pytest tests/ -v --cov=app --cov-report=term
   ```

3. **Integration Tests** (5-10 minutes)
   Ask if they want to test against:
   - Mock services (local Docker)
   - Real APIs (if available)
   - Staging environment

   Provide appropriate commands for their choice.

4. **End-to-End Test** (30 seconds)
   ```bash
   # With mocks
   ./demo-realistic-workflow.sh

   # With real APIs (if configured)
   ./demo-realistic-workflow.sh --real-apis
   ```

5. **GitLab Pipeline Test**
   Show how to verify the pipeline will pass:
   - Run linting locally
   - Run tests locally
   - Check Helm chart: `helm lint ./helm`

After running, summarize:
- Tests passed/failed
- Coverage percentage
- Any issues found
- Next steps if failures
