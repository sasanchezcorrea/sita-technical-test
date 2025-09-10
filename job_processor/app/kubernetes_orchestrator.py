"""Kubernetes job orchestration service."""

import logging
from typing import Optional, List
from datetime import datetime
import json

from kubernetes import client, config
from kubernetes.client.rest import ApiException

try:
    from .models import JobRequest, JobResult, JobStatus, TenantConfig, ModuleConfig
    from .config import settings
except ImportError:
    # Fallback for standalone execution
    from models import JobRequest, JobResult, JobStatus, TenantConfig, ModuleConfig  # type: ignore[import-untyped]
    from config import settings  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


class KubernetesOrchestrator:
    """Orchestrates optimization jobs in Kubernetes."""

    def __init__(self):
        """Initialize Kubernetes client."""
        try:
            if settings.in_cluster:
                config.load_incluster_config()
            else:
                config.load_kube_config()

            self.v1 = client.CoreV1Api()
            self.batch_v1 = client.BatchV1Api()
            self.rbac_v1 = client.RbacAuthorizationV1Api()

            logger.info("Kubernetes client initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Kubernetes client: %s", e)
            raise

    async def create_namespace_if_not_exists(self, namespace: str) -> bool:
        """Create namespace if it doesn't exist."""
        try:
            self.v1.read_namespace(name=namespace)
            logger.info("Namespace %s already exists", namespace)
            return True
        except ApiException as e:
            if e.status == 404:
                # Create namespace
                namespace_body = client.V1Namespace(
                    metadata=client.V1ObjectMeta(
                        name=namespace,
                        labels={
                            "app.kubernetes.io/managed-by": "optiflight-coordinator",
                            "optiflight.sita.aero/tenant": namespace.replace(
                                "airline-", ""
                            ),
                        },
                    )
                )

                try:
                    self.v1.create_namespace(body=namespace_body)
                    logger.info("Created namespace: %s", namespace)
                    return True
                except ApiException as create_error:
                    logger.error(
                        "Failed to create namespace %s: %s", namespace, create_error
                    )
                    return False
            else:
                logger.error("Error checking namespace %s: %s", namespace, e)
                return False

    async def create_resource_quota(
        self, namespace: str, tenant_config: TenantConfig
    ) -> bool:
        """Create resource quota for tenant namespace."""
        try:
            quota_name = f"{namespace}-quota"

            # Default resource limits if not specified
            default_quota = {
                "requests.cpu": "2",
                "requests.memory": "4Gi",
                "limits.cpu": "8",
                "limits.memory": "16Gi",
                "pods": str(tenant_config.max_parallel_executions * 2),
                "persistentvolumeclaims": "10",
            }

            # Merge with tenant-specific quotas
            resource_quota = {**default_quota, **tenant_config.resource_quota}

            quota_body = client.V1ResourceQuota(
                metadata=client.V1ObjectMeta(
                    name=quota_name,
                    namespace=namespace,
                    labels={
                        "app.kubernetes.io/managed-by": "optiflight-coordinator",
                        "optiflight.sita.aero/tenant": tenant_config.airline,
                    },
                ),
                spec=client.V1ResourceQuotaSpec(hard=resource_quota),
            )

            try:
                self.v1.create_namespaced_resource_quota(
                    namespace=namespace, body=quota_body
                )
                logger.info("Created resource quota for namespace: %s", namespace)
                return True
            except ApiException as e:
                if e.status == 409:  # Already exists
                    logger.info(
                        "Resource quota already exists for namespace: %s", namespace
                    )
                    return True
                else:
                    logger.error("Failed to create resource quota: %s", e)
                    return False

        except Exception as e:
            logger.error("Error creating resource quota for %s: %s", namespace, e)
            return False

    def _create_job_spec(
        self, job_request: JobRequest, module_config: ModuleConfig, namespace: str
    ) -> client.V1Job:
        """Create Kubernetes Job specification."""
        job_name = f"optim-{job_request.airline}-{job_request.job_id[:8]}"

        # Environment variables
        env_vars = [
            client.V1EnvVar(name="JOB_ID", value=job_request.job_id),
            client.V1EnvVar(name="EVENT_TYPE", value=job_request.event_type),
            client.V1EnvVar(
                name="EVENT_DATA", value=json.dumps(job_request.event_data)
            ),
            client.V1EnvVar(name="AIRLINE", value=job_request.airline),
        ]

        # Add module-specific environment variables
        for key, value in module_config.env_vars.items():
            env_vars.append(client.V1EnvVar(name=key, value=value))

        # Resource requirements
        resources = client.V1ResourceRequirements(
            requests={
                "cpu": module_config.cpu_request,
                "memory": module_config.memory_request,
            },
            limits={
                "cpu": module_config.cpu_limit,
                "memory": module_config.memory_limit,
            },
        )

        # Container specification
        container = client.V1Container(
            name="optimization-module",
            image=f"{module_config.image}:{module_config.version}",
            env=env_vars,
            resources=resources,
            image_pull_policy="Always",
        )

        # Pod specification
        pod_spec = client.V1PodSpec(
            containers=[container],
            restart_policy="Never",
            active_deadline_seconds=job_request.timeout_seconds
            or module_config.timeout_seconds,
        )

        # Pod template
        pod_template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={
                    "app": "optiflight-optimization",
                    "job-id": job_request.job_id,
                    "airline": job_request.airline,
                    "module": module_config.name,
                    "optiflight.sita.aero/tenant": job_request.airline,
                }
            ),
            spec=pod_spec,
        )

        # Job specification
        job_spec = client.V1JobSpec(
            template=pod_template,
            backoff_limit=3,
            completions=1,
            parallelism=1,
            ttl_seconds_after_finished=3600,  # Clean up after 1 hour
        )

        # Job object
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(
                name=job_name,
                namespace=namespace,
                labels={
                    "app": "optiflight-optimization",
                    "job-id": job_request.job_id,
                    "airline": job_request.airline,
                    "module": module_config.name,
                    "optiflight.sita.aero/tenant": job_request.airline,
                },
            ),
            spec=job_spec,
        )

        return job

    async def submit_job(
        self, job_request: JobRequest, module_config: ModuleConfig, namespace: str
    ) -> JobResult:
        """Submit optimization job to Kubernetes."""
        try:
            # Ensure namespace exists
            await self.create_namespace_if_not_exists(namespace)

            # Create job specification
            job = self._create_job_spec(job_request, module_config, namespace)

            # Submit job
            result = self.batch_v1.create_namespaced_job(namespace=namespace, body=job)

            logger.info("Job %s submitted to namespace %s", job_request.job_id, namespace)

            return JobResult(
                job_id=job_request.job_id,
                status=JobStatus.PENDING,
                started_at=datetime.utcnow(),
                pod_name=result.metadata.name,
                namespace=namespace,
            )

        except ApiException as e:
            logger.error("Failed to submit job %s: %s", job_request.job_id, e)
            return JobResult(
                job_id=job_request.job_id,
                status=JobStatus.FAILED,
                error_message=str(e),
                namespace=namespace,
            )

    async def get_job_status(self, job_id: str, namespace: str) -> Optional[JobResult]:
        """Get status of a running job."""
        try:
            # Find job by label selector
            jobs = self.batch_v1.list_namespaced_job(
                namespace=namespace, label_selector=f"job-id={job_id}"
            )

            if not jobs.items:
                return None

            job = jobs.items[0]

            # Determine job status
            status = JobStatus.PENDING
            if job.status.active:
                status = JobStatus.RUNNING
            elif job.status.succeeded:
                status = JobStatus.COMPLETED
            elif job.status.failed:
                status = JobStatus.FAILED

            # Calculate duration
            duration = None
            if job.status.start_time and job.status.completion_time:
                duration = (
                    job.status.completion_time - job.status.start_time
                ).total_seconds()

            return JobResult(
                job_id=job_id,
                status=status,
                started_at=job.status.start_time,
                completed_at=job.status.completion_time,
                duration_seconds=duration,
                pod_name=job.metadata.name,
                namespace=namespace,
            )

        except ApiException as e:
            logger.error("Failed to get job status for %s: %s", job_id, e)
            return None

    async def cancel_job(self, job_id: str, namespace: str) -> bool:
        """Cancel a running job."""
        try:
            jobs = self.batch_v1.list_namespaced_job(
                namespace=namespace, label_selector=f"job-id={job_id}"
            )

            if not jobs.items:
                return False

            job_name = jobs.items[0].metadata.name

            # Delete the job
            self.batch_v1.delete_namespaced_job(
                name=job_name, namespace=namespace, propagation_policy="Background"
            )

            logger.info("Job %s cancelled in namespace %s", job_id, namespace)
            return True

        except ApiException as e:
            logger.error("Failed to cancel job %s: %s", job_id, e)
            return False

    async def list_active_jobs(
        self, namespace: Optional[str] = None
    ) -> List[JobResult]:
        """List all active jobs."""
        try:
            if namespace:
                jobs = self.batch_v1.list_namespaced_job(namespace=namespace)
            else:
                jobs = self.batch_v1.list_job_for_all_namespaces()

            active_jobs = []
            for job in jobs.items:
                if job.status.active:  # Only active jobs
                    job_id = job.metadata.labels.get("job-id", "unknown")
                    active_jobs.append(
                        JobResult(
                            job_id=job_id,
                            status=JobStatus.RUNNING,
                            started_at=job.status.start_time,
                            pod_name=job.metadata.name,
                            namespace=job.metadata.namespace,
                        )
                    )

            return active_jobs

        except ApiException as e:
            logger.error("Failed to list active jobs: %s", e)
            return []
