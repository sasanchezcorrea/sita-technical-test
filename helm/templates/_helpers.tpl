{{/*
Expand the name of the chart.
*/}}
{{- define "optiflight-coordinator.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "optiflight-coordinator.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "optiflight-coordinator.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "optiflight-coordinator.labels" -}}
helm.sh/chart: {{ include "optiflight-coordinator.chart" . }}
{{ include "optiflight-coordinator.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/component: job-processor
optiflight.sita.aero/tier: control-plane
{{- end }}

{{/*
Selector labels
*/}}
{{- define "optiflight-coordinator.selectorLabels" -}}
app.kubernetes.io/name: {{ include "optiflight-coordinator.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "optiflight-coordinator.serviceAccountName" -}}
{{- if .Values.rbac.create }}
{{- default (include "optiflight-coordinator.fullname" .) .Values.rbac.serviceAccountName }}
{{- else }}
{{- default "default" .Values.rbac.serviceAccountName }}
{{- end }}
{{- end }}

{{/*
Create database URL for PostgreSQL
*/}}
{{- define "optiflight-coordinator.databaseUrl" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "postgresql://%s:%s@%s-postgresql:5432/%s" .Values.postgresql.auth.username .Values.postgresql.auth.password .Release.Name .Values.postgresql.auth.database }}
{{- end }}
{{- end }}

{{/*
Create Redis URL
*/}}
{{- define "optiflight-coordinator.redisUrl" -}}
{{- if .Values.redis.enabled }}
{{- if .Values.redis.auth.enabled }}
{{- printf "redis://:%s@%s-redis-master:6379" .Values.redis.auth.password .Release.Name }}
{{- else }}
{{- printf "redis://%s-redis-master:6379" .Release.Name }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create Kafka brokers URL
*/}}
{{- define "optiflight-coordinator.kafkaBrokers" -}}
{{- if .Values.kafka.enabled }}
{{- printf "%s-kafka:9092" .Release.Name }}
{{- end }}
{{- end }}

{{/*
Common tenant labels
*/}}
{{- define "optiflight-coordinator.tenantLabels" -}}
app.kubernetes.io/managed-by: {{ .Release.Service }}
optiflight.sita.aero/managed-by: optiflight-coordinator
{{- end }}
