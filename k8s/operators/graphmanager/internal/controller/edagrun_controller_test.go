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

package controller_test

import (
	"context"
	"fmt"
	"path/filepath"
	"runtime"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/client-go/kubernetes/scheme"
	"k8s.io/client-go/rest"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/envtest"
	logf "sigs.k8s.io/controller-runtime/pkg/log"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	edagv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
)

var cfg *rest.Config
var k8sClient client.Client
var testEnv *envtest.Environment

var _ = Describe("EDAGRun Controller", func() {
	BeforeEach(func() {
		logf.SetLogger(zap.New(zap.WriteTo(GinkgoWriter), zap.UseDevMode(true)))

		By("bootstrapping test environment")
		testEnv = &envtest.Environment{
			CRDDirectoryPaths:     []string{filepath.Join("..", "..", "config", "crd", "bases")},
			ErrorIfCRDPathMissing: true,

			// The BinaryAssetsDirectory is only required if you want to run the tests directly
			// without call the makefile target test. If not informed it will look for the
			// default path defined in controller-runtime which is /usr/local/kubebuilder/.
			// Note that you must have the required binaries setup under the bin directory to perform
			// the tests directly. When we run make test it will be setup and used automatically.
			BinaryAssetsDirectory: filepath.Join("..", "..", "bin", "k8s",
				fmt.Sprintf("1.29.0-%s-%s", runtime.GOOS, runtime.GOARCH)),
		}

		var err error
		// cfg is defined in this file globally.
		cfg, err = testEnv.Start()
		Expect(err).NotTo(HaveOccurred())
		Expect(cfg).NotTo(BeNil())

		err = graphv1alpha1.AddToScheme(scheme.Scheme)
		Expect(err).NotTo(HaveOccurred())

		//+kubebuilder:scaffold:scheme

		k8sClient, err = client.New(cfg, client.Options{Scheme: scheme.Scheme})
		Expect(err).NotTo(HaveOccurred())
		Expect(k8sClient).NotTo(BeNil())

	})

	AfterEach(func() {
		By("tearing down the test environment")
		err := testEnv.Stop()
		Expect(err).NotTo(HaveOccurred())
	})

	Context("When reconciling a resource", func() {
		const resourceName = "test-resource"

		ctx := context.Background()

		typeNamespacedName := types.NamespacedName{
			Name:      resourceName,
			Namespace: "default", // TODO(user):Modify as needed
		}
		edagrun := &edagv1alpha1.EDAGRun{}

		BeforeEach(func() {
			By("creating the custom resource for the Kind EDAGRun")
			err := k8sClient.Get(ctx, typeNamespacedName, edagrun)
			if err != nil && errors.IsNotFound(err) {
				resource := &edagv1alpha1.EDAGRun{
					ObjectMeta: metav1.ObjectMeta{
						Name:      resourceName,
						Namespace: "default",
					},
					// TODO(user): Specify other spec details if needed.
				}
				Expect(k8sClient.Create(ctx, resource)).To(Succeed())
			}
		})

		AfterEach(func() {
			// TODO(user): Cleanup logic after each test, like removing the resource instance.
			resource := &edagv1alpha1.EDAGRun{}
			err := k8sClient.Get(ctx, typeNamespacedName, resource)
			Expect(err).NotTo(HaveOccurred())

			By("Cleanup the specific resource instance EDAGRun")
			Expect(k8sClient.Delete(ctx, resource)).To(Succeed())
		})

		// It("should successfully reconcile the resource", func() {
		// 	By("Reconciling the created resource")
		// 	controllerReconciler := controller.EDAGRunReconciler{
		// 		Client: k8sClient,
		// 		Scheme: k8sClient.Scheme(),
		// 	}

		// 	_, err := controllerReconciler.Reconcile(ctx, reconcile.Request{
		// 		NamespacedName: typeNamespacedName,
		// 	})
		// 	Expect(err).NotTo(HaveOccurred())
		// 	// TODO(user): Add more specific assertions depending on your controller's reconciliation logic.
		// 	// Example: If you expect a certain status condition after reconciliation, verify it here.
		// })
	})
})
