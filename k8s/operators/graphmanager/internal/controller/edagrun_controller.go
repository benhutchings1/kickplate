/*
Copyright 2024.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package controller

import (
	"context"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
)

// EDAGRunReconciler reconciles a ExecutionGraphRun object
type EDAGRunReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

//+kubebuilder:rbac:groups=graph.kickplate.com,resources=executiongraphruns,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=graph.kickplate.com,resources=executiongraphruns/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=graph.kickplate.com,resources=executiongraphruns/finalizers,verbs=update

func (r *EDAGRunReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := log.FromContext(ctx)

	run_resource := &graphv1alpha1.EDAGRun{}

	if err := r.FetchResource(ctx, req.NamespacedName, run_resource); err != nil {
		log.Info("Aborting reconcile, assuming resource has been deleted")
	}

	// TODO(user): your logic here
	// Check if status is known, initialise object
	// 	Change status to unknown
	// 	refetch resource
	// Add finaliser if not already
	// Check if marked for delete
	// Check if job exists
	// After any change make physical change make sure to refetch

	return ctrl.Result{}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *EDAGRunReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&graphv1alpha1.EDAGRun{}).
		Complete(r)
}
