package integrationtests_test

import (
	"context"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	controller "github.com/benhutchings1/kickplate/internal/controller"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/client-go/kubernetes/scheme"
	"sigs.k8s.io/controller-runtime/pkg/reconcile"
)

var _ = Describe("EDAGRun Controller", Ordered, func() {
	simpleedag := new(graphv1alpha1.EDAG)
	simpleedagrun := new(graphv1alpha1.EDAGRun)
	reconciler := new(controller.EDAGRunReconciler)

	BeforeEach(func() {
		reconciler = &controller.EDAGRunReconciler{
			Client: k8sClient,
			Scheme: scheme.Scheme,
		}
	})

	Context("resolving a simple EDAG", func() {
		By("creating simple edag")
		simpleedag = &graphv1alpha1.EDAG{
			ObjectMeta: metav1.ObjectMeta{
				Name:      "simpleedag",
				Namespace: SampleDefaultInputs.Namespace,
			},
			Spec: graphv1alpha1.EDAGSpec{
				Steps: map[string]graphv1alpha1.EDAGStep{
					"simplestep1": {
						Image:    "simpleimage",
						Replicas: int32(3),
						Envs: map[string]string{
							"simple": "value",
						},
						Args: []string{
							"args", "input",
						},
					},
				},
			},
		}

		Expect(k8sClient.Create(ctx, simpleedag)).To(Succeed())

		By("creating edagrun to resolve")
		simpleedagrun = &graphv1alpha1.EDAGRun{
			ObjectMeta: metav1.ObjectMeta{
				Name:      "simpleedagrun",
				Namespace: SampleDefaultInputs.Namespace,
			},
			Spec: graphv1alpha1.EDAGRunSpec{
				EDAGName: "simpleedag",
			},
		}

		It("should create jobs for simple edagrun with 1 step", func() {
			request := reconcile.Request{NamespacedName: types.NamespacedName{
				Name: simpleedagrun.Name, Namespace: SampleDefaultInputs.Namespace,
			}}
			result, err := reconciler.Reconcile(context.TODO(), request)
		})

	})
})
