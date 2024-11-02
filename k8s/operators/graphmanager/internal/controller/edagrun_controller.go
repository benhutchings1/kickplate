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

	batchv1 "k8s.io/api/batch/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	"github.com/benhutchings1/kickplate/internal/clusterclient"
	"github.com/benhutchings1/kickplate/internal/service"
)

// EDAGRunReconciler reconciles a ExecutionGraphRun object
type EDAGRunReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

// +kubebuilder:rbac:groups=graph.kickplate.com,resources=EDAG,verbs=get;list
// +kubebuilder:rbac:groups=graph.kickplate.com,resources=EDAGRuns,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=graph.kickplate.com,resources=EDAGRuns/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=graph.kickplate.com,resources=EDAGRuns/finalizers,verbs=update
// +kubebuilder:rbac:groups=core,resources=events,verbs=create;patch
// +kubebuilder:rbac:groups=apps,resources=jobs,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=core,resources=pods,verbs=get;list;watch
// +kubebuilder:rbac:groups=graph.kickplate.com,resources=executiongraphruns,verbs=get;list;watch;create;update;patch;delete
func (r *EDAGRunReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	// Higher V logging level indicates higher warning level
	// Rough guidelines
	// V0 - Checking and other debugging information
	// V1 - Creating/Updating resources
	// V2 - unexpected outcome/failures
	log := log.FromContext(ctx)
	log.V(0).Info("Detected change, running reconcile")

	config, err := LoadConfig()
	if err != nil {
		log.Error(err, "Failed to load config")
		panic("Failed to load config")
	}

	svc := &service.EDAGRunService{
		Client: clusterclient.EDAGRunClient{
			ClusterClient: r.Client,
			Scheme:        r.Scheme,
			Log:           &log,
		},
		Log: &log,
	}

	run, err := svc.FetchEDAGRun(ctx, req.NamespacedName)
	if err != nil {
		return ctrl.Result{}, nil
	}

	edagName := types.NamespacedName{
		Namespace: config.Namespace,
		Name:      run.Spec.EDAGName,
	}
	edag, err := svc.FetchEDAG(ctx, edagName)
	if err != nil {
		return ctrl.Result{}, nil
	}

	if err = svc.CheckRunOwnerReference(edag, run); err != nil {
		return ctrl.Result{}, nil
	}

	if complete := svc.IsRunComplete(run); complete {
		return ctrl.Result{}, nil
	}

	if isFailed, err := svc.StartNewJobs(
		ctx, run, edag, config.Namespace, config.DefaultPortpod, config.DefaultPodLabels,
	); err != nil {
		return ctrl.Result{}, err
	} else if isFailed {
		return ctrl.Result{}, nil
	}

	return ctrl.Result{}, nil
}

func (r *EDAGRunReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&graphv1alpha1.EDAGRun{}).
		Owns(&batchv1.Job{}).
		Complete(r)
}
