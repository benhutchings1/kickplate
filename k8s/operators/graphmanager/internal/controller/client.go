package controller

import (
	"context"
	"fmt"

	apierrors "k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"
)

func (r *EDAGRunReconciler) FetchResource(ctx context.Context, key types.NamespacedName, obj client.Object) error {
	log := log.FromContext(ctx)
	err := r.Get(ctx, key, obj)
	if err != nil {
		if apierrors.IsNotFound(err) {
			log.Info(fmt.Sprintf("Could not fetch %s resource", obj), key)
			return err
		}
	}
	return nil
}

func (r *EDAGRunReconciler) SetResourceStatus(
	condition_pointer *[]metav1.Condition,
	newCondition metav1.Condition,
	ctx context.Context,
	key types.NamespacedName,
	obj client.Object) error {

}
