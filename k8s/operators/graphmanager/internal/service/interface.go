package service

import (
	"context"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	batchv1 "k8s.io/api/batch/v1"
	"k8s.io/apimachinery/pkg/types"
)

type ServiceManager interface {
	CreateJob(
		ctx context.Context,
		edag *graphv1alpha1.EDAG,
		run *graphv1alpha1.EDAGRun,
		stepname string,
		stepSpec graphv1alpha1.EDAGStep,
		namespace string,
		podPort int32,
		defaultLabels map[string]string,
	) error

	StartNewJobs(
		ctx context.Context,
		run *graphv1alpha1.EDAGRun,
		edag *graphv1alpha1.EDAG,
		namespace string,
		podPort int32,
		defaultLabels map[string]string,
	) (isFailed bool, err error)

	CheckRunOwnerReference(
		ctx context.Context,
		edag *graphv1alpha1.EDAG,
		run *graphv1alpha1.EDAGRun,
	) error

	IsRunComplete(run *graphv1alpha1.EDAGRun) bool

	FetchEDAG(
		ctx context.Context,
		edagNamespacedName types.NamespacedName,
	) (edag *graphv1alpha1.EDAG, err error)

	FetchEDAGRun(
		ctx context.Context,
		edagRunNamespacedName types.NamespacedName,
	) (edagrun *graphv1alpha1.EDAGRun, err error)

	IsJobComplete(job *batchv1.Job) bool
}
