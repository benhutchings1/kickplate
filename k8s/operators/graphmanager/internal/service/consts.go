package service

import (
	batchv1 "k8s.io/api/batch/v1"
)

// Initial condition of jobs
const JobInitialising batchv1.JobConditionType = "Initialising"

type RunStatus string

const (
	RunFailed     RunStatus = "Failed"
	RunSucceeded  RunStatus = "Succeeded"
	RunInProgress RunStatus = "InProgress"
)
