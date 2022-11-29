{{/*
Expand the name of the chart.
*/}}
{{- define "tca.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "tca.fullname" -}}
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
{{- define "tca.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "tca.labels" -}}
helm.sh/chart: {{ include "tca.chart" . }}
{{ include "tca.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "tca.selectorLabels" -}}
app.kubernetes.io/name: {{ include "tca.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "tca.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
    {{- default (include "tca.fullname" .) .Values.serviceAccount.name }}
{{- else }}
    {{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create a default fully qualified mongodb subchart.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "tca.mariadb.fullname" -}}
{{- if .Values.mariadb.fullnameOverride -}}
    {{- .Values.mariadb.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
    {{- $name := default "mariadb" .Values.mariadb.nameOverride -}}
    {{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "tca.redis.fullname" -}}
{{- if .Values.redis.fullnameOverride -}}
    {{ $name := .Values.redis.fullnameOverride | trunc 63 | trimSuffix "-"}}
    {{- list $name "master" | join "-" -}}
{{- else -}}
    {{- $name := default "redis" .Values.redis.nameOverride -}}
    {{- printf "%s-%s-master" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{/*
Redis config
*/}}
{{- define "tca.redis.host" -}}
{{- if eq .Values.redis.enabled true -}}
    {{- ( include "tca.redis.fullname" . ) -}}
{{- else -}}
    {{- .Values.externalRedis.host -}}
{{- end -}}
{{- end -}}

{{- define "tca.redis.port" -}}
{{- if eq .Values.redis.enabled true -}}
    {{- printf "6379" -}}
{{- else -}}
    {{- printf "%d" ( .Values.externalRedis.port | int ) -}}
{{- end -}}
{{- end -}}

{{- define "tca.redis.password" -}}
{{- if eq .Values.redis.enabled true -}}
    {{- .Values.redis.auth.password -}}
{{- else -}}
    {{- .Values.externalRedis.password -}}
{{- end -}}
{{- end -}}

{{/*
DB config
*/}}
{{- define "tca.database.host" -}}
{{- if eq .Values.mariadb.enabled true -}}
    {{- ( include "tca.mariadb.fullname" . ) -}}
{{- else -}}
    {{- .Values.externalMySQL.host -}}
{{- end -}}
{{- end -}}

{{- define "tca.database.port" -}}
{{- if eq .Values.mariadb.enabled true -}}
    {{- printf "3306" -}}
{{- else -}}
    {{- printf "%d" (.Values.externalMySQL.port | int ) -}}
{{- end -}}
{{- end -}}

{{- define "tca.database.username" -}}
{{- if eq .Values.mariadb.enabled true -}}
    {{- printf "root" -}}
{{- else -}}
    {{- .Values.externalMySQL.username -}}
{{- end -}}
{{- end -}}

{{- define "tca.database.password" -}}
{{- if eq .Values.mariadb.enabled true -}}
    {{- .Values.mariadb.auth.rootPassword -}}
{{- else -}}
    {{- .Values.externalMySQL.password -}}
{{- end -}}
{{- end -}}
