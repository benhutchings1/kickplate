{{- define "common.labels" -}}
{{ .Values.labelsCommon | toYaml }}
{{- end -}}