package clusterclient

import (
	"context"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	"github.com/go-logr/logr"
	apierrors "k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/api/meta"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
)

type EDAGRunClient struct {
	ClusterClient client.Client
	Scheme        *runtime.Scheme
	Log           *logr.Logger
}

func (client *EDAGRunClient) FetchResource(
	ctx context.Context,
	key types.NamespacedName,
	obj client.Object,
	LogError bool,
) error {
	client.Log.V(2).Info("Fetching resource", "name", key.Name)

	if err := client.ClusterClient.Get(ctx, key, obj); err != nil {
		if apierrors.IsNotFound(err) {
			if LogError {
				client.Log.Error(err, "Could not fetch resource", "name", key.Name)
			} else {
				client.Log.V(1).Info("Could not fetch resource", "name", key.Name)
			}
			return err
		}
		return err
	}

	return nil
}

func (client *EDAGRunClient) UpdateResources(
	ctx context.Context,
	obj client.Object,
) error {
	client.Log.V(1).Info("Updating resource", "resource", obj.GetName())
	if err := client.ClusterClient.Update(ctx, obj); err != nil {
		client.Log.Error(err, "Failed to update resource", "resource", obj.GetName())
		return err
	}
	return nil
}

func (client *EDAGRunClient) UpdateStatus(
	ctx context.Context,
	run *graphv1alpha1.EDAGRun,
	newCondition metav1.Condition,
) error {
	client.Log.V(1).Info("Updating run status", "run", run.Name)
	meta.SetStatusCondition(
		&run.Status.Conditions,
		newCondition,
	)

	if err := client.ClusterClient.Status().Update(ctx, run); err != nil {
		client.Log.Error(err, "Failed to update resource status", "resource_name", run.Name)
		return err
	}
	return nil

}

func (client *EDAGRunClient) CreateJob(ctx context.Context, obj client.Object) error {
	return client.ClusterClient.Create(ctx, obj)
}

func (client *EDAGRunClient) SetControllerReference(
	parentObj client.Object,
	childObj client.Object,
) error {
	if err := ctrl.SetControllerReference(parentObj, childObj, client.Scheme); err != nil {
		client.Log.Error(
			err, "Failed to set controller reference",
			"ParentObject", parentObj.GetName(), "ChildObject", childObj.GetName(),
		)
	}
	return nil
}
