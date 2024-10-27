package controller

import (
	"context"
	"fmt"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	"github.com/benhutchings1/kickplate/builders"
	batchv1 "k8s.io/api/batch/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/log"
)

func (r *EDAGRunReconciler) CreateJob(
	ctx context.Context,
	edag *graphv1alpha1.EDAG,
	run *graphv1alpha1.EDAGRun,
	stepname string,
	stepSpec graphv1alpha1.EDAGStep,
	namespace string,
	podPort int32,
	defaultLabels map[string]string,
) error {
	log := log.FromContext(ctx)

	jobName := fmt.Sprintf("%s-%s", edag.Name, stepname)
	log.Info("Creating job", "jobName", jobName, "jobNamespace", namespace)

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

	run.Status.Jobs[stepname] = jobName

	if err := ctrl.SetControllerReference(&graphv1alpha1.EDAGRun{}, newJob, r.Scheme); err != nil {
		return err
	}

	log.Info("Finished creating new job", "jobName", jobName, "jobNamespace", namespace)
	return nil
}

func (r *EDAGRunReconciler) StartNewJobs(ctx context.Context, run *graphv1alpha1.EDAGRun, edag *graphv1alpha1.EDAG, namespace string, podPort int32, defaultLabels map[string]string) (isFailed bool, err error) {
	jobs, err := r.fetchJobs(ctx, run, edag, namespace)

	if err != nil {
		return false, err
	}

	// Check if any failed first before starting new jobs
	for stepname, _ := range jobs {
		job := jobs[stepname]
		status := getLatestJobCondition(job)

		if status.Type == batchv1.JobFailed || status.Type == batchv1.JobFailureTarget {
			return true, nil
		}
	}

	for stepname, job := range jobs {
		if job == nil || !isJobComplete(job) {
			if checkIfDependentsAreFinished(stepname, &jobs) {
				stepSpec := edag.Spec.Steps[stepname]
				if err := r.CreateJob(
					ctx, edag, run, stepname, stepSpec, namespace, podPort, defaultLabels,
				); err != nil {
					return false, err
				}
			}
		}

	}
	return false, nil
}

func checkIfDependentsAreFinished(stepName string, jobs *map[string]*batchv1.Job) bool {
	return true
}

func (r *EDAGRunReconciler) fetchJobs(ctx context.Context, run *graphv1alpha1.EDAGRun, edag *graphv1alpha1.EDAG, namespace string) (map[string]*batchv1.Job, error) {
	jobs := map[string]*batchv1.Job{}

	for stepname, _ := range edag.Spec.Steps {
		jobName, exists := run.Status.Jobs[stepname]

		if exists {
			job := batchv1.Job{}
			if err := r.FetchResource(
				ctx, types.NamespacedName{Name: jobName, Namespace: namespace}, &job, true,
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

func CheckRunOwnerReferences() error {
	return nil
}

func isJobComplete(job *batchv1.Job) bool {
	condition := getLatestJobCondition(job)
	return condition.Type == batchv1.JobComplete || condition.Type == batchv1.JobFailed
}

func IsRunComplete(run *graphv1alpha1.EDAGRun) bool {
	condition := getLatestRunCondition(run)
	return condition.Type == string(RunFailed) || condition.Type == string(RunSucceeded)
}

func getLatestJobCondition(job *batchv1.Job) batchv1.JobCondition {
	conditions := job.Status.Conditions
	return conditions[len(conditions)-1]
}

func getLatestRunCondition(run *graphv1alpha1.EDAGRun) metav1.Condition {
	conditions := run.Status.Conditions
	return conditions[len(conditions)-1]
}
