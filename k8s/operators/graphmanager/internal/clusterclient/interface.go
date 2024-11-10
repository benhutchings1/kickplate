package clusterclient

import (
	"context"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	"github.com/go-logr/logr"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	"sigs.k8s.io/controller-runtime/pkg/client"
)

type ClusterClientManager interface {
	client.Client
	*runtime.Scheme
	*logr.Logger

	FetchResource(
		ctx context.Context,
		key types.NamespacedName,
		obj client.Object,
	) (isfound bool, err error)
	UpdateResources(
		ctx context.Context,
		obj client.Object,
	) error
	UpdateStatus(
		ctx context.Context,
		run *graphv1alpha1.EDAGRun,
		newCondition metav1.Condition,
	) error
	CreateJob(ctx context.Context, obj client.Object) error
	SetControllerReference(
		ctx context.Context,
		parentObj client.Object,
		childObj client.Object,
	) error
}
