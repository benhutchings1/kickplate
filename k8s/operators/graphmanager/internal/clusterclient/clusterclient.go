package clusterclient

import (
	"context"
	"errors"

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

var IsNotFoundFn = apierrors.IsNotFound
var SetControllerReferenceFn = ctrl.SetControllerReference

type ClusterClient struct {
	K8sClient client.Client
	Scheme    *runtime.Scheme
	Log       *logr.Logger
}

func (client *ClusterClient) FetchResource(
	ctx context.Context,
	key types.NamespacedName,
	obj client.Object,
) (isfound bool, err error) {
	client.Log.V(2).Info("Fetching resource", "name", key.Name)
	if err := client.K8sClient.Get(ctx, key, obj); err != nil {
		if IsNotFoundFn(err) {
			return false, err
		} else {
			return false, nil
		}
	}
	return true, nil
}

func (client *ClusterClient) UpdateResources(
	ctx context.Context,
	obj client.Object,
) error {
	client.Log.V(1).Info("Updating resource", "resource", obj.GetName())
	if err := client.K8sClient.Update(ctx, obj); err != nil {
		client.Log.Error(err, "Failed to update resource", "resource", obj.GetName())
		return err
	}
	return nil
}

func (client *ClusterClient) UpdateStatus(
	ctx context.Context,
	run *graphv1alpha1.EDAGRun,
	newCondition metav1.Condition,
) error {
	client.Log.V(1).Info("Updating run status", "run", run.Name)
	meta.SetStatusCondition(
		&run.Status.Conditions,
		newCondition,
	)

	status := client.K8sClient.Status()

	if err := status.Update(ctx, run); err != nil {
		client.Log.Error(err, "Failed to update resource status", "resource_name", run.Name)
		return err
	}
	return nil
}

func (client *ClusterClient) CreateJob(ctx context.Context, obj client.Object) error {
	return client.K8sClient.Create(ctx, obj)
}

func (client *ClusterClient) SetControllerReference(
	ctx context.Context,
	parentObj client.Object,
	childObj client.Object,
) error {
	client.Log.Info(
		"Setting controller reference",
		"ParentObject", parentObj.GetName(), "ChildObject", childObj.GetName(),
	)

	if parentObj.GetObjectKind() == childObj.GetObjectKind() &&
		parentObj.GetName() == childObj.GetName() {
		errormsg := "an object cannot reference itself"
		err := errors.New(errormsg)
		client.Log.Error(
			err, errormsg,
			"ParentKind", parentObj.GetObjectKind(),
			"ChildKind", childObj.GetObjectKind(),
			"ParentName", parentObj.GetName(),
			"ChildName", childObj.GetName(),
		)
		return err
	}

	if err := SetControllerReferenceFn(childObj, parentObj, client.Scheme); err != nil {
		client.Log.Error(
			err, "Failed to set controller reference",
			"parent", parentObj.GetName(), "child", childObj.GetName(),
		)
	}
	if err := client.UpdateResources(ctx, parentObj); err != nil {
		return err
	}
	return nil
}
