package controller

import (
	"context"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	"github.com/go-logr/logr"
	apierrors "k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/api/meta"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	"sigs.k8s.io/controller-runtime/pkg/client"
)

func (r *EDAGRunReconciler) FetchResource(
	log *logr.Logger,
	ctx context.Context,
	key types.NamespacedName,
	obj client.Object,
	logError bool,
) error {
	log.V(2).Info("Fetching resource", "name", key.Name)

	if err := r.Get(ctx, key, obj); err != nil {
		if apierrors.IsNotFound(err) {
			if logError {
				log.Error(err, "Could not fetch resource", "name", key.Name)
			} else {
				log.V(1).Info("Could not fetch resource", "name", key.Name)
			}
			return err
		}
		return err
	}

	return nil
}

func (r *EDAGRunReconciler) UpdateResources(
	log *logr.Logger,
	ctx context.Context,
	obj client.Object,
) error {
	log.V(1).Info("Updating resource", "resource", obj.GetName())
	if err := r.Update(ctx, obj); err != nil {
		log.Error(err, "Failed to update resource", "resource", obj.GetName())
		return err
	}
	return nil
}

func (r *EDAGRunReconciler) UpdateStatus(
	log *logr.Logger,
	ctx context.Context,
	run *graphv1alpha1.EDAGRun,
	newCondition metav1.Condition,
) error {
	log.V(1).Info("Updating run status", "run", run.Name)
	meta.SetStatusCondition(
		&run.Status.Conditions,
		newCondition,
	)

	if err := r.Status().Update(ctx, run); err != nil {
		log.Error(err, "Failed to update resource status", "resource_name", run.Name)
		return err
	}
	return nil

}
