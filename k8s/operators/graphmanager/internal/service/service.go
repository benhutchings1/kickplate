package service

import (
	"context"
	"errors"
	"fmt"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	"github.com/benhutchings1/kickplate/builders"
	"github.com/benhutchings1/kickplate/internal/clusterclient"
	"github.com/go-logr/logr"
	batchv1 "k8s.io/api/batch/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
)

type EDAGRunService struct {
	Client clusterclient.ClusterClientManager
	Log    *logr.Logger
}

func (svc *EDAGRunService) CreateJob(
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
	svc.Log.V(1).Info("Creating job", "jobName", jobName, "jobNamespace", namespace)

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
		Args:          stepSpec.Args,
		UserUUID:      1000,
		Envs:          envs,
	}
	newJob := builder.BuildJob()

	if err := svc.Client.CreateJob(ctx, newJob); err != nil {
		svc.Log.Error(err, "Failed to create job",
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
	if err := svc.Client.UpdateStatus(ctx, run, newCondition); err != nil {
		return err
	}

	if err := svc.Client.SetControllerReference(
		ctx, run, newJob,
	); err != nil {
		return nil
	}

	return nil
}

func (svc *EDAGRunService) StartNewJobs(
	ctx context.Context,
	run *graphv1alpha1.EDAGRun,
	edag *graphv1alpha1.EDAG,
	namespace string,
	podPort int32,
	defaultLabels map[string]string,
) (isFailed bool, err error) {
	svc.Log.V(2).Info("Checking for new jobs to start")
	jobs, err := svc.fetchJobs(ctx, run, edag, namespace)

	if err != nil {
		return false, err
	}

	// Check if any failed first before starting new jobs
	// Also check if run has finished
	if failed, finished := svc.checkJobsFailedOrFinished(jobs); failed {
		return true, nil
	} else if finished {
		return false, nil
	}

	for stepname, job := range jobs {
		if job == nil {
			if checkIfDependentsAreFinished(stepname, &jobs, edag) {
				stepSpec := edag.Spec.Steps[stepname]
				if err := svc.CreateJob(
					ctx, edag, run, stepname, stepSpec, namespace, podPort, defaultLabels,
				); err != nil {
					return false, err
				}
			}
		}
	}
	return false, nil
}

func (svc *EDAGRunService) checkJobsFailedOrFinished(
	jobs map[string]*batchv1.Job,
) (failed bool, finished bool) {
	finished = true
	failed = false
	for stepname := range jobs {
		job := jobs[stepname]
		if job != nil && isJobFailed(job) {
			svc.Log.V(0).Info("Found failed job", "job", job.Name)
			failed = true
		} else if job == nil || !IsJobComplete(job) {
			finished = false
		}
	}
	return failed, finished
}

func (svc *EDAGRunService) fetchJobs(
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
			if found, err := svc.Client.FetchResource(
				ctx, types.NamespacedName{Name: jobName, Namespace: namespace}, &job,
			); err != nil {
				svc.Log.Error(err, "Could not fetch resource", "name", jobName)
				return nil, err
			} else if !found {
				svc.Log.V(1).Info("Could not fetch resource", "name", jobName)
			}
			jobs[stepname] = &job
		} else {
			jobs[stepname] = nil
		}
	}
	return jobs, nil
}

func (svc *EDAGRunService) CheckRunOwnerReference(
	ctx context.Context,
	edag *graphv1alpha1.EDAG,
	run *graphv1alpha1.EDAGRun,
) error {
	svc.Log.V(2).Info("Checking owner references", "edag", edag.Name, "edagrun", run.Name)
	if edag.OwnerReferences != nil {
		for _, ref := range edag.OwnerReferences {
			if ref.Kind == "EDAGRun" && ref.Name == run.Name {
				svc.Log.V(2).Info(
					"Found owner reference", "Edag Name", edag.Name, "Edagrun name", run.Name,
				)
				return nil
			}
		}
	}
	svc.Log.V(1).Info("Creating owner reference", "Edag Name", edag.Name, "Edagrun name", run.Name)
	if err := svc.Client.SetControllerReference(
		ctx, edag, run,
	); err != nil {
		svc.Log.Error(
			err,
			"Failed to check owner references",
			"Edag Name",
			edag.Name,
			"Edagrun name",
			run.Name,
		)
		return err
	}
	return nil
}

func (svc *EDAGRunService) IsRunComplete(run *graphv1alpha1.EDAGRun) bool {
	conditions := run.Status.Conditions

	if conditions == nil || len(conditions) == 0 {
		return false
	}

	latestCondition := conditions[len(conditions)-1]
	complete := latestCondition.Type == string(RunFailed) ||
		latestCondition.Type == string(RunSucceeded)
	if complete {
		svc.Log.V(0).Info("Run already complete")
	}
	return complete
}

func (svc *EDAGRunService) FetchEDAG(
	ctx context.Context,
	edagNamespacedName types.NamespacedName,
) (*graphv1alpha1.EDAG, error) {
	fetchedEdag := &graphv1alpha1.EDAG{}
	if found, err := svc.Client.FetchResource(ctx, edagNamespacedName, fetchedEdag); err != nil || !found {
		if !found {
			err = errors.New("failed retrieve EDAG")
		}
		svc.Log.Error(
			err, "EDAG cannot be retrieved",
			"namespace", edagNamespacedName.Namespace, "name", edagNamespacedName.Name,
		)
		return nil, err
	}
	return fetchedEdag, nil
}

func (svc *EDAGRunService) FetchEDAGRun(
	ctx context.Context,
	edagRunNamespacedName types.NamespacedName,
) (*graphv1alpha1.EDAGRun, error) {
	fetchedEdagrun := &graphv1alpha1.EDAGRun{}
	if found, err := svc.Client.FetchResource(ctx, edagRunNamespacedName, fetchedEdagrun); err != nil ||
		!found {
		svc.Log.V(0).Info(
			"Aborting reconcile, assuming EDAGRun has been deleted",
			"name", edagRunNamespacedName.Name, "namespace", edagRunNamespacedName.Namespace,
		)
		return nil, err
	}
	return fetchedEdagrun, nil
}

func checkIfDependentsAreFinished(
	stepName string,
	jobs *map[string]*batchv1.Job,
	edag *graphv1alpha1.EDAG,
) bool {
	stepSpec := edag.Spec.Steps[stepName]
	if stepSpec.Dependencies == nil || len(stepSpec.Dependencies) == 0 {
		return true
	}

	for _, dependentStepname := range stepSpec.Dependencies {
		dependentJob := (*jobs)[dependentStepname]
		if dependentJob == nil || !IsJobComplete(dependentJob) {
			return false
		}
	}

	return true
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
