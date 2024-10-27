package controller

import (
	"context"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	apierrors "k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/api/meta"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
	"sigs.k8s.io/controller-runtime/pkg/log"
)

func (r *EDAGRunReconciler) FetchResource(ctx context.Context, key types.NamespacedName, obj client.Object, logError bool) error {
	log := log.FromContext(ctx)
	log.Info("Fetching %s resource", "name", key.Name)

	if err := r.Get(ctx, key, obj); err != nil {
		if apierrors.IsNotFound(err) {
			if logError {
				log.Error(err, "Could not fetch resource", "name", key.Name)
			} else {
				log.Info("Could not fetch resource", "name", key.Name)
			}
			return err
		}
		return err
	}
	log.Info("Finished fetching resource", "name", key.Name)
	return nil
}

func (r *EDAGRunReconciler) AddFinalizer(
	obj client.Object,
	newFinalizer string,
	ctx context.Context,
) (error, bool) {
	log := log.FromContext(ctx)

	log.Info("creating finalizer")

	if complete := controllerutil.AddFinalizer(obj, newFinalizer); !complete {
		log.Error(nil, "Failed to add finaliser to resource", "resource_name", obj.GetName())
		return nil, true
	}

	if err := r.UpdateResources(obj, ctx); err != nil {
		log.Error(err, "Failed to update resource finaliser", "resource_name", obj.GetName())
		return err, false
	}

	log.Info("Finished creating finaliser")

	return nil, false
}

func (r *EDAGRunReconciler) RemoveFinalizer(
	obj client.Object,
	finalizer string,
	ctx context.Context,
) bool {
	log := log.FromContext(ctx)
	if complete := controllerutil.RemoveFinalizer(obj, finalizer); !complete {
		log.Error(nil, "Failed to remove finaliser", "resource_name", obj.GetName())
		return true
	}

	return false
}

func (r *EDAGRunReconciler) UpdateResources(obj client.Object, ctx context.Context) error {
	log := log.FromContext(ctx)
	if err := r.Update(ctx, obj); err != nil {
		log.Error(err, "Failed to update resource", "resource_name", "obj.GetName()")
		return err
	}
	return nil
}

func (r *EDAGRunReconciler) UpdateStatus(
	ctx context.Context, edagrun *graphv1alpha1.EDAGRun, newCondition metav1.Condition,
) error {
	log := log.FromContext(ctx)

	meta.SetStatusCondition(
		&edagrun.Status.Conditions,
		newCondition,
	)

	if err := r.Status().Update(ctx, edagrun); err != nil {
		log.Error(err, "Failed to update resource status", "resource_name", edagrun.Name)
		return err
	}
	return nil

}
