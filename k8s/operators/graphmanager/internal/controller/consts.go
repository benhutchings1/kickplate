package controller

import (
	batchv1 "k8s.io/api/batch/v1"
)

// Initial condition of pods
const JobInitialising batchv1.JobConditionType = "Initialising"
