package controller

import (
	"context"
	"fmt"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	"github.com/benhutchings1/kickplate/builders"
	"github.com/go-logr/logr"
	batchv1 "k8s.io/api/batch/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	ctrl "sigs.k8s.io/controller-runtime"
)

func (r *EDAGRunReconciler) CreateJob(
	log *logr.Logger,
	ctx context.Context,
	edag *graphv1alpha1.EDAG,
	run *graphv1alpha1.EDAGRun,
	stepname string,
	stepSpec graphv1alpha1.EDAGStep,
	namespace string,
	podPort int32,
	defaultLabels map[string]string,
) error {
	jobName := fmt.Sprintf("%s-%s", run.Name, stepname)
	log.V(1).Info("Creating job", "jobName", jobName, "jobNamespace", namespace)

	envs := []corev1.EnvVar{}
	for name, value := range stepSpec.Envs {
		envs = append(envs,
			corev1.EnvVar{Name: name, Value: value},
		)
	}

	labels := defaultLabels
	labels["app"] = "kickplate"
	labels["edag"] = edag.Name

	builder := builders.JobBuilder{
		Name:          jobName,
		Namespace:     namespace,
		Labels:        labels,
		Image:         stepSpec.Image,
		Port:          podPort,
		Completions:   stepSpec.Replicas,
		Paralellism:   stepSpec.Replicas,
		Indexed:       batchv1.IndexedCompletion,
		RestartPolicy: corev1.RestartPolicyNever,
		Command:       stepSpec.Command,
		UserUUID:      1000,
		Envs:          envs,
	}
	newJob := builder.BuildJob()

	if err := r.Create(ctx, newJob); err != nil {
		log.Error(err, "Failed to create job",
			"jobName", jobName,
			"namespace", namespace,
		)
		return err
	}

	if run.Status.Jobs == nil {
		run.Status.Jobs = map[string]string{}
	}

	newCondition := metav1.Condition{
		Type: string(RunInProgress), Status: metav1.ConditionTrue,
		Reason: "JobStart", Message: fmt.Sprintf("Created %s", jobName),
	}

	run.Status.Jobs[stepname] = jobName
	if err := r.UpdateStatus(log, ctx, run, newCondition); err != nil {
		return err
	}

	if err := ctrl.SetControllerReference(&graphv1alpha1.EDAGRun{}, newJob, r.Scheme); err != nil {
		return err
	}

	return nil
}

func (r *EDAGRunReconciler) StartNewJobs(
	log *logr.Logger,
	ctx context.Context,
	run *graphv1alpha1.EDAGRun,
	edag *graphv1alpha1.EDAG,
	namespace string,
	podPort int32,
	defaultLabels map[string]string,
) (isFailed bool, err error) {
	log.V(2).Info("Checking for new jobs to start")
	jobs, err := r.fetchJobs(log, ctx, run, edag, namespace)

	if err != nil {
		return false, err
	}

	// Check if any failed first before starting new jobs
	for stepname := range jobs {
		job := jobs[stepname]
		if job != nil && isJobFailed(job) {
			log.V(0).Info("Found failed job", "job", job.Name)
			return true, nil
		}
	}

	for stepname, job := range jobs {
		if job == nil {
			if checkIfDependentsAreFinished(stepname, &jobs, edag) {
				stepSpec := edag.Spec.Steps[stepname]
				if err := r.CreateJob(
					log, ctx, edag, run, stepname, stepSpec, namespace, podPort, defaultLabels,
				); err != nil {
					return false, err
				}
			}
		}
	}
	return false, nil
}

func checkIfDependentsAreFinished(
	stepName string,
	jobs *map[string]*batchv1.Job,
	edag *graphv1alpha1.EDAG,
) bool {
	stepSpec := edag.Spec.Steps[stepName]
	if stepSpec.Dependencies == nil {
		return true
	}

	for _, dependentStepname := range stepSpec.Dependencies {
		if !IsJobComplete((*jobs)[dependentStepname]) {
			return false
		}
	}

	return true
}

func (r *EDAGRunReconciler) fetchJobs(
	log *logr.Logger,
	ctx context.Context,
	run *graphv1alpha1.EDAGRun,
	edag *graphv1alpha1.EDAG,
	namespace string,
) (map[string]*batchv1.Job, error) {
	jobs := map[string]*batchv1.Job{}

	for stepname := range edag.Spec.Steps {
		jobName, exists := run.Status.Jobs[stepname]

		if exists {
			job := batchv1.Job{}
			if err := r.FetchResource(
				log, ctx, types.NamespacedName{Name: jobName, Namespace: namespace}, &job, true,
			); err != nil {
				return nil, err
			}
			jobs[stepname] = &job
		} else {
			jobs[stepname] = nil
		}
	}
	return jobs, nil
}

func (r *EDAGRunReconciler) CheckRunOwnerReference(
	log *logr.Logger,
	edag *graphv1alpha1.EDAG,
	run *graphv1alpha1.EDAGRun,
) error {

	// NOT WORKING
	log.V(2).Info("Checking owner references", "edag", edag.Name, "edagrun", run.Name)
	if run.OwnerReferences != nil {
		for _, ref := range run.OwnerReferences {
			if ref.Kind == "EDAG" && ref.Name == edag.Name {
				log.V(2).Info("Found owner reference")
				return nil
			}
		}
	}
	log.V(1).Info("Creating owner reference")
	if err := ctrl.SetControllerReference(edag, run, r.Scheme); err != nil {
		return err
	}
	return nil
}

func IsRunComplete(run *graphv1alpha1.EDAGRun) bool {
	conditions := run.Status.Conditions

	if conditions == nil || len(conditions) == 0 {
		return false
	}

	latestCondition := conditions[len(conditions)-1]
	return latestCondition.Type == string(RunFailed) || latestCondition.Type == string(RunSucceeded)
}

func isJobFailed(job *batchv1.Job) (failed bool) {
	conditions := job.Status.Conditions

	if conditions == nil || len(conditions) == 0 {
		return false
	}

	latestStatus := conditions[len(conditions)-1]

	if latestStatus.Type == batchv1.JobFailed || latestStatus.Type == batchv1.JobFailureTarget {
		return true
	}
	return false
}

func IsJobComplete(job *batchv1.Job) bool {
	return job.Status.Active == 0
}
