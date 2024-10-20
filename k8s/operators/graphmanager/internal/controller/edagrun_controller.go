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
	"k8s.io/apimachinery/pkg/api/meta"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
	"sigs.k8s.io/controller-runtime/pkg/log"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	"github.com/benhutchings1/kickplate/builders"
)

// EDAGRunReconciler reconciles a ExecutionGraphRun object
type EDAGRunReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

//+kubebuilder:rbac:groups=graph.kickplate.com,resources=executiongraphruns,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=graph.kickplate.com,resources=executiongraphruns/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=graph.kickplate.com,resources=executiongraphruns/finalizers,verbs=update
//+kubebuilder:rbac:groups=core,resources=events,verbs=create;patch
//+kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=core,resources=pods,verbs=get;list;watch

func (r *EDAGRunReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	// Logging V levels
	// 0 = Critical, 1 = Error, 2 = Warning, 3 = Info, 4 = Debug
	log := log.FromContext(ctx)
	log.Info("Detected change, running reconcile")

	edagrun := &graphv1alpha1.EDAGRun{}
	if err := r.FetchResource(ctx, req.NamespacedName, edagrun); err != nil {
		log.Info("Aborting reconcile, assuming EDAGRun has been deleted")
		return ctrl.Result{}, nil
	}

	if edagrun.Status.Conditions == nil || len(edagrun.Status.Conditions) == 0 {
		log.Info("Setting status condition to Initialising")
		meta.SetStatusCondition(
			&edagrun.Status.Conditions,
			metav1.Condition{
				Type:    EDAGUnknown,
				Status:  metav1.ConditionUnknown,
				Reason:  "Initialising",
				Message: "Initialising EDAGRun deployment",
			},
		)

		if err := r.Status().Update(ctx, edagrun); err != nil {
			log.Error(err, "Failed to update resource status", "resource_name", edagrun.Name)
			return ctrl.Result{}, err
		}

		log.Info("Finished updating status condition")

		// refetch to avoid 'resource is busy' error
		if err := r.FetchResource(ctx, req.NamespacedName, edagrun); err != nil {
			return ctrl.Result{}, err
		}
	}

	if !controllerutil.ContainsFinalizer(edagrun, edagFinalizer) {
		if err, requeue := r.AddFinalizer(edagrun, edagFinalizer, ctx); err != nil {
			return ctrl.Result{}, err
		} else if requeue {
			log.Info("Requeuing")
			return ctrl.Result{Requeue: true}, nil
		}
		log.Info("Finished making finalizer")
	}

	if edagrun.GetDeletionTimestamp() != nil {
		if err, requeue := r.DoEDAGFinalisation(edagrun, ctx); err != nil {
			return ctrl.Result{}, err
		} else if requeue {
			return ctrl.Result{Requeue: true}, nil
		}
	}

	childDeployments := &appsv1.Deployment{}
	deploymentNamespacedName := types.NamespacedName{Name: "testing", Namespace: "default"}
	if err := r.FetchResource(ctx, deploymentNamespacedName, childDeployments); err != nil {
		log.Info("Could not fetch deployment, creating new deployment")
		if err := r.CreateDeployment(childDeployments, ctx, *edagrun); err != nil {
			return ctrl.Result{}, err
		}
	}

	if err, requeue := r.EnsureDeploymentMatchesSpec(childDeployments, edagrun, ctx); err != nil {
		return ctrl.Result{}, err
	} else if requeue {
		return ctrl.Result{Requeue: true}, nil
	}

	return ctrl.Result{}, nil
}

func (r *EDAGRunReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&graphv1alpha1.EDAGRun{}).
		Owns(&appsv1.Deployment{}).
		Complete(r)
}

func (r *EDAGRunReconciler) DoEDAGFinalisation(obj client.Object, ctx context.Context) (error, bool) {
	log := log.FromContext(ctx)

	log.Info("Removing Finaliser")
	if do_requeue := r.RemoveFinalizer(obj, edagFinalizer, ctx); do_requeue {
		return nil, true
	}

	if err := r.UpdateResources(obj, ctx); err != nil {
		return err, false
	}
	log.Info("Finished removing finaliser")

	return nil, false
}

func (r *EDAGRunReconciler) CreateDeployment(obj client.Object, ctx context.Context, EDAGRun graphv1alpha1.EDAGRun) error {
	log := log.FromContext(ctx)

	deployment_name := "testing"
	deployment_namespace := "default"
	log.Info("Creating deployment", "deployment_name", deployment_name, "namespace", deployment_namespace)

	builder := builders.DeploymentBuilder{
		Name:      deployment_name,
		Namespace: deployment_namespace,
		Replicas:  EDAGRun.Spec.Size,
		Labels:    map[string]string{"app": "kickplate"},
		Image:     "nginx:latest",
		Port:      int32(8000),
	}
	deployment := builder.BuildDeployment()

	if err := r.Create(ctx, deployment); err != nil {
		log.Error(err, "Failed to create deployment",
			"deployment_name", deployment_name,
			"namespace", deployment_namespace,
		)
		return err
	}

	if err := ctrl.SetControllerReference(&EDAGRun, deployment, r.Scheme); err != nil {
		return err
	}

	log.Info("Finished creating deployment")
	return nil
}

func (r *EDAGRunReconciler) EnsureDeploymentMatchesSpec(deployment *appsv1.Deployment, EDAGRun *graphv1alpha1.EDAGRun, ctx context.Context) (error, bool) {
	log := log.FromContext(ctx)

	if *deployment.Spec.Replicas == EDAGRun.Spec.Size {
		log.Info("Deployment matches state")
		return nil, false
	}

	log.Info(
		"Updating deployment to correct size",
		"resource_name", deployment.ObjectMeta.Name,
		"actual_size", *deployment.Spec.Replicas,
		"expected_size", &EDAGRun.Spec.Size,
	)
	deployment.Spec.Replicas = &EDAGRun.Spec.Size

	if err := r.UpdateResources(deployment, ctx); err != nil {
		return err, false
	}

	return nil, true
}
