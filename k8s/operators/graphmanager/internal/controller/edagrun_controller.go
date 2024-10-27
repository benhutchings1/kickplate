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

	appsv1 "k8s.io/api/apps/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
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

//+kubebuilder:rbac:groups=graph.kickplate.com,resources=EDAGRuns,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=graph.kickplate.com,resources=EDAGRuns/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=graph.kickplate.com,resources=EDAGRuns/finalizers,verbs=update
//+kubebuilder:rbac:groups=core,resources=events,verbs=create;patch
//+kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=core,resources=pods,verbs=get;list;watch
//+kubebuilder:rbac:groups=graph.kickplate.com,resources=executiongraphruns,verbs=get;list;watch;create;update;patch;delete

func (r *EDAGRunReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := log.FromContext(ctx)
	log.Info("Detected change, running reconcile")

	config, err := LoadConfig()
	if err != nil {
		panic("Failed to load config")
	}

	run := &graphv1alpha1.EDAGRun{}
	if err := r.FetchResource(ctx, req.NamespacedName, run, true); err != nil {
		log.Info("Aborting reconcile, assuming EDAGRun has been deleted")
		return ctrl.Result{}, nil
	}

	edag := &graphv1alpha1.EDAG{}
	edagName := types.NamespacedName{
		Namespace: config.Namespace,
		Name:      run.Spec.EDAGName,
	}
	if err := r.FetchResource(ctx, edagName, edag, true); err != nil {
		log.Error(err, "EDAG cannot be retrieved", "namespace", edagName.Namespace, "name", edagName.Name)
		return ctrl.Result{}, nil
	}

	if err := CheckRunOwnerReferences(); err != nil {
		return ctrl.Result{}, nil
	}

	if complete := IsRunComplete(run); complete {
		log.Info("Run already complete")
		return ctrl.Result{}, nil
	}

	if isFailed, err := r.StartNewJobs(ctx, run, edag, config.Namespace, config.DefaultPortpod, config.DefaultPodLabels); err != nil {
		return ctrl.Result{}, err
	} else if isFailed {
		log.Info("Run has falied")
		return ctrl.Result{}, nil
	}

	return ctrl.Result{}, nil
}

func (r *EDAGRunReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&graphv1alpha1.EDAGRun{}).
		Owns(&appsv1.Deployment{}).
		Complete(r)
}
