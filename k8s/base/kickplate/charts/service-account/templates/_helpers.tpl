{{- define "common.labels" -}}
{{ .Values.labelsCommon | toYaml }}
{{- end -}}

{{- define "role.parser" -}}
{{- $readerRoles := list "get" "describe" "list" "watch" -}}
{{- $contributorRoles := list "get" "describe" "list" "watch" "create" "patch" "update" -}}
{{- $ownerRoles := list "get" "describe" "list" "watch" "create" "patch" "update" "delete" "deleteCollection" -}}
{{- $roleMap := dict "reader" $readerRoles "contributor" $contributorRoles "owner" $ownerRoles -}}
{{- if not (eq .verbs nil) -}}
{{ .verbs }}
{{- else -}}
{{ index $roleMap .role }}
{{- end -}}
{{- end -}}