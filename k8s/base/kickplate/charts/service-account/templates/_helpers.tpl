{{- define "common.labels" -}}
{{ .Values.labelsCommon | toYaml }}
{{- end -}}

{{- define "role.parser" -}}
{{- $readerRoles := list "get" "list" "watch"  -}}
{{- $contributorRoles := list "get" "list" "watch" "create" "patch" "update" -}}
{{- $ownerRoles := list "get" "list" "watch" "create" "patch" "update" "delete" "deleteCollection" -}}
{{- $roleMap := dict "reader" $readerRoles "contributor" $contributorRoles "owner" $ownerRoles -}}
{{- index $roleMap .role | toYaml | nindent 6 -}}
{{- end -}}