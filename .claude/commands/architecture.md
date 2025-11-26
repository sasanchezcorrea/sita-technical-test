---
description: Explain OptiFlight architecture
---

Provide an architecture overview based on what the user is asking about:

1. **High-Level Overview**
   - OptiFlight Coordinator (this system)
   - External services (OptiCore, Freya Climb, Freya Level)
   - Infrastructure components
   - Data flow

2. **Component Deep Dives**
   If user asks about specific components, explain:

   **Coordinator:**
   - Multi-tenant job processing
   - Event-driven architecture (Kafka/RabbitMQ)
   - Kubernetes orchestration
   - OptiCoordinator versioning (Phase 12)

   **External Services:**
   - OptiCore: Initial flight optimization
   - Freya Climb: ML-enhanced climb predictions
   - Freya Level: ML-enhanced cruise predictions
   - Circuit breaker & retry logic

   **Infrastructure:**
   - Kubernetes clusters (staging/preprod/prod)
   - PostgreSQL primary + read replicas
   - Redis cluster for caching
   - Message queues (Kafka/RabbitMQ)

   **Observability:**
   - ELK Stack for logs
   - Prometheus + Grafana for metrics
   - Jaeger for distributed tracing
   - OpenTelemetry instrumentation

3. **Data Flow**
   Explain the complete optimization flow:
   ```
   OptiCore (initial) → Freya Climb (ML) → Freya Level (ML)
   → OptiCoordinator (selection) → OptiCore (final)
   → Database (materialization)
   ```

4. **Visual Diagrams**
   - Reference `architecture/sita.drawio`
   - Reference `docs/guides/ARCHITECTURE-FLOW-GUIDE.md`
   - Reference `ARCHITECTURE-DIAGRAM-SUMMARY.md`

Use ASCII diagrams or mermaid syntax if helpful.
Keep explanations concise and developer-friendly.
