{{- define "common.labels" -}}
{{ .Values.global.commonLabels | toYaml }}
{{- end -}}
