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
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"
)

func (r *EDAGRunReconciler) InitialiseEDAGRun(ctx context.Context, edagrun *graphv1alpha1.EDAGRun, edag *graphv1alpha1.EDAG) error {
	log := log.FromContext(ctx)

	log.Info("Initialising edagrun", "runName", edagrun.Name)

	for _, step := range edag.Spec.Steps {
		edagrun.Status.JobDetails = append(
			edagrun.Status.JobDetails,
			graphv1alpha1.JobDetail{
				Stepname:        step.Name,
				Jobname:         fmt.Sprintf("%s-%s", edagrun.Name, step.Name),
				Status:          string(batchv1.JobSuspended),
				JobDependencies: step.Dependencies,
			},
		)
	}

	if err := r.UpdateStatus(
		ctx, edagrun, metav1.Condition{
			Type:    string(JobInitialising),
			Status:  metav1.ConditionUnknown,
			Reason:  "Initialising",
			Message: "Initialising EDAGRun executions",
		},
	); err != nil {
		return err
	}

	log.Info("Finished initialising")
	return nil
}

func (r *EDAGRunReconciler) DoEDAGFinalisation(obj client.Object, ctx context.Context, finalizer string) (error, bool) {
	log := log.FromContext(ctx)

	log.Info("Removing Finaliser")
	if do_requeue := r.RemoveFinalizer(obj, finalizer, ctx); do_requeue {
		return nil, true
	}

	if err := r.UpdateResources(obj, ctx); err != nil {
		return err, false
	}
	log.Info("Finished removing finaliser")

	return nil, false
}

func (r *EDAGRunReconciler) CreateJob(ctx context.Context, stepDescription graphv1alpha1.EDAGStep, namespacedName types.NamespacedName) error {
	log := log.FromContext(ctx)

	log.Info("Creating job", "jobName", namespacedName.Name, "jobNamespace", namespacedName.Namespace)

	builder := builders.JobBuilder{
		Name:          namespacedName.Name,
		Namespace:     namespacedName.Namespace,
		Labels:        map[string]string{"app": "kickplate"},
		Image:         "nginx:latest",
		Port:          int32(8000),
		Completions:   stepDescription.Replicas,
		Paralellism:   stepDescription.Replicas,
		Indexed:       batchv1.IndexedCompletion,
		RestartPolicy: corev1.RestartPolicyNever,
		Command:       stepDescription.Command,
		UserUUID:      1000,
		Envs: []corev1.EnvVar{
			{Name: "APP_ENV", Value: "PROD"},
		},
	}
	newJob := builder.BuildJob()

	if err := r.Create(ctx, newJob); err != nil {
		log.Error(err, "Failed to create job",
			"deployment_name", namespacedName.Name,
			"namespace", namespacedName.Namespace,
		)
		return err
	}

	if err := ctrl.SetControllerReference(&graphv1alpha1.EDAGRun{}, newJob, r.Scheme); err != nil {
		return err
	}

	log.Info("Finished creating new job", "jobName", namespacedName.Name, "jobNamespace", namespacedName.Namespace)
	return nil
}

func (r *EDAGRunReconciler) UpdateJobStatus(ctx context.Context, edagrun *graphv1alpha1.EDAGRun, runNamespace string) (map[string]graphv1alpha1.JobDetail, error) {
	log := log.FromContext(ctx)
	updatedStatus := map[string]graphv1alpha1.JobDetail{}
	newStatus := []graphv1alpha1.JobDetail{}

	for _, jobStatus := range edagrun.Status.JobDetails {
		job := &batchv1.Job{}
		if err := r.FetchResource(ctx, types.NamespacedName{
			Namespace: runNamespace,
			Name:      jobStatus.Jobname,
		}, job, true); err != nil {
			log.Error(err, "Failed to get job", "jobname", jobStatus.Jobname, "namespace", runNamespace)
			return nil, err
		}
		conditions := job.Status.Conditions
		jobStatus.Status = string(conditions[len(conditions)-1].Type)

		updatedStatus[jobStatus.Stepname] = jobStatus
		newStatus = append(newStatus, jobStatus)
	}

	edagrun.Status.JobDetails = newStatus
	if err := r.UpdateResources(edagrun, ctx); err != nil {
		return nil, err
	}

	return updatedStatus, nil
}
