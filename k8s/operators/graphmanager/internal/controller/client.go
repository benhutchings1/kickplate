package controller

import (
	"context"
	"fmt"

	apierrors "k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/types"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
	"sigs.k8s.io/controller-runtime/pkg/log"
)

func (r *EDAGRunReconciler) FetchResource(ctx context.Context, key types.NamespacedName, obj client.Object) error {
	log := log.FromContext(ctx)
	log.Info(fmt.Sprintf("Fetching %s resource", obj.GetName()))

	err := r.Get(ctx, key, obj)
	if err != nil {
		if apierrors.IsNotFound(err) {
			log.Error(err, "Could not fetch resource", "resource", key)
			return err
		}
		return err
	}
	log.Info("Finished fetching resource", "resource", obj.GetName())
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
