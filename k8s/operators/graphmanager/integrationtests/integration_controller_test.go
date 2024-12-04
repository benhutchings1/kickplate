package integrationtests_test

import (
	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	controller "github.com/benhutchings1/kickplate/internal/controller"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	batchv1 "k8s.io/api/batch/v1"
	corev1 "k8s.io/api/core/v1"
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
		BeforeAll(func() {
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
			Expect(k8sClient.Create(ctx, simpleedagrun)).To(Succeed())

			By("creating overriding config values")
			var mockLoadConfigFn = func() (config controller.Config) {
				return controller.Config{
					Namespace:      SampleDefaultInputs.Namespace,
					FinaliserPath:  "graph.kickplate.com/finalizer",
					DefaultPortpod: 8000,
					DefaultPodLabels: map[string]string{
						"label": "default",
					},
				}
			}
			controller.LoadConfigFn = mockLoadConfigFn
		})

		AfterAll(func() {
			By("cleaning up simple reconcile test")
			Expect(k8sClient.Delete(ctx, simpleedag)).To(Succeed())
			Expect(k8sClient.Delete(ctx, simpleedagrun)).To(Succeed())
		})

		It("should create jobs for edag with 1 step", func() {
			request := reconcile.Request{NamespacedName: types.NamespacedName{
				Name: "simpleedagrun", Namespace: SampleDefaultInputs.Namespace,
			}}

			result, err := reconciler.Reconcile(ctx, request)
			Expect(err).ToNot(HaveOccurred())
			Expect(result.Requeue).To(BeFalse())

			job := batchv1.Job{}
			expectedjobname := "simpleedagrun-simplestep1"

			Expect(k8sClient.Get(
				ctx,
				types.NamespacedName{
					Name: expectedjobname, Namespace: SampleDefaultInputs.Namespace,
				},
				&job,
			)).To(Succeed())
			compareJobWithEdagStep(*simpleedag, "simplestep1", job)
		})
	})
})

func compareJobWithEdagStep(edag graphv1alpha1.EDAG, stepname string, job batchv1.Job) {
	jobContainer := job.Spec.Template.Spec.Containers[0]
	edagstep := edag.Spec.Steps[stepname]
	completionMode := batchv1.IndexedCompletion

	Expect(jobContainer.Image).To(Equal(edagstep.Image))
	Expect(job.Spec.Completions).To(Equal(&edagstep.Replicas))
	Expect(job.Spec.Parallelism).To(Equal(&edagstep.Replicas))
	Expect(job.Spec.CompletionMode).To(Equal(&completionMode))
	Expect(jobContainer.Command).To(Equal(edagstep.Command))
	Expect(jobContainer.Args).To(Equal(edagstep.Args))
	Expect(job.Spec.Template.Spec.RestartPolicy).To(Equal(corev1.RestartPolicyNever))
	Expect(jobContainer.Env).To(Equal(convertEnvspec(edagstep.Envs)))
}

func convertEnvspec(envspec map[string]string) []corev1.EnvVar {
	envs := []corev1.EnvVar{}
	for name, value := range envspec {
		envs = append(envs,
			corev1.EnvVar{Name: name, Value: value},
		)
	}
	return envs
}
