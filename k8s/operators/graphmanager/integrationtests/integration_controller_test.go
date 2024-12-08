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
	reconciler := new(controller.EDAGRunReconciler)

	BeforeEach(func() {
		reconciler = &controller.EDAGRunReconciler{
			Client: k8sClient,
			Scheme: scheme.Scheme,
		}
	})

	BeforeAll(func() {
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
	Context("resolving an EDAG with two parallel steps", func() {
		twostepedag := new(graphv1alpha1.EDAG)
		twostepedagrun := new(graphv1alpha1.EDAGRun)

		BeforeAll(func() {
			By("creating EDAG with two parallel steps")
			twostepedag = &graphv1alpha1.EDAG{
				ObjectMeta: metav1.ObjectMeta{
					Name:      "twostepedag",
					Namespace: SampleDefaultInputs.Namespace,
				},
				Spec: graphv1alpha1.EDAGSpec{
					Steps: map[string]graphv1alpha1.EDAGStep{
						"step1": {
							Image:    "image1",
							Replicas: int32(1),
							Envs: map[string]string{
								"step": "1",
							},
							Args: []string{
								"args1", "input1",
							},
							Command: []string{
								"optional", "command1",
							},
						},
						"step2": {
							Image:    "image2",
							Replicas: int32(2),
							Envs: map[string]string{
								"step": "2",
							},
							Args: []string{
								"args2", "input2",
							},
							Command: []string{
								"optional", "command2",
							},
						},
					},
				},
			}
			Expect(k8sClient.Create(ctx, twostepedag)).To(Succeed())

			By("creating edagrun to resolve")
			twostepedagrun = &graphv1alpha1.EDAGRun{
				ObjectMeta: metav1.ObjectMeta{
					Name:      "twostepedagrun",
					Namespace: SampleDefaultInputs.Namespace,
				},
				Spec: graphv1alpha1.EDAGRunSpec{
					EDAGName: "twostepedag",
				},
			}
			Expect(k8sClient.Create(ctx, twostepedagrun)).To(Succeed())
		})

		AfterAll(func() {
			By("cleaning up simple reconcile test")
			Expect(k8sClient.Delete(ctx, twostepedag)).To(Succeed())
			Expect(k8sClient.Delete(ctx, twostepedagrun)).To(Succeed())
		})

		It("should create jobs for edag with two parallel steps", func() {
			request := reconcile.Request{NamespacedName: types.NamespacedName{
				Name: "twostepedagrun", Namespace: SampleDefaultInputs.Namespace,
			}}

			result, err := reconciler.Reconcile(ctx, request)
			Expect(err).ToNot(HaveOccurred())
			Expect(result.Requeue).To(BeFalse())

			job1 := new(batchv1.Job)
			job2 := new(batchv1.Job)
			expectedjob1name := "twostepedagrun-step1"
			expectedjob2name := "twostepedagrun-step2"

			Expect(k8sClient.Get(
				ctx,
				types.NamespacedName{
					Name: expectedjob1name, Namespace: SampleDefaultInputs.Namespace,
				},
				job1,
			)).To(Succeed())
			compareJobWithEdagStep(*twostepedag, "step1", *job1)

			Expect(k8sClient.Get(
				ctx,
				types.NamespacedName{
					Name: expectedjob2name, Namespace: SampleDefaultInputs.Namespace,
				},
				job2,
			)).To(Succeed())
			compareJobWithEdagStep(*twostepedag, "step2", *job2)
		})
	})

	Context("resolving an EDAG with two sequential steps", func() {
		sequentialstepsedag := new(graphv1alpha1.EDAG)
		sequentialstepsedagrun := new(graphv1alpha1.EDAGRun)

		BeforeAll(func() {
			By("creating EDAG with two sequential steps")
			sequentialstepsedag = &graphv1alpha1.EDAG{
				ObjectMeta: metav1.ObjectMeta{
					Name:      "sequentialstepsedag",
					Namespace: SampleDefaultInputs.Namespace,
				},
				Spec: graphv1alpha1.EDAGSpec{
					Steps: map[string]graphv1alpha1.EDAGStep{
						"step1": {
							Image:    "image1",
							Replicas: int32(1),
							Envs: map[string]string{
								"step": "1",
							},
							Args: []string{
								"args1", "input1",
							},
							Command: []string{
								"optional", "command1",
							},
						},
						"step2": {
							Image:    "image2",
							Replicas: int32(2),
							Envs: map[string]string{
								"step": "2",
							},
							Args: []string{
								"args2", "input2",
							},
							Command: []string{
								"optional", "command2",
							},
							Dependencies: []string{
								"step1",
							},
						},
					},
				},
			}
			Expect(k8sClient.Create(ctx, sequentialstepsedag)).To(Succeed())

			By("creating edagrun to resolve")
			sequentialstepsedagrun = &graphv1alpha1.EDAGRun{
				ObjectMeta: metav1.ObjectMeta{
					Name:      "sequentialstepsedagrun",
					Namespace: SampleDefaultInputs.Namespace,
				},
				Spec: graphv1alpha1.EDAGRunSpec{
					EDAGName: "sequentialstepsedag",
				},
			}
			Expect(k8sClient.Create(ctx, sequentialstepsedagrun)).To(Succeed())
		})

		AfterAll(func() {
			By("cleaning up simple reconcile test")
			Expect(k8sClient.Delete(ctx, sequentialstepsedag)).To(Succeed())
			Expect(k8sClient.Delete(ctx, sequentialstepsedagrun)).To(Succeed())
		})

		It("should create jobs for edag with two sequential steps", func() {
			request := reconcile.Request{NamespacedName: types.NamespacedName{
				Name: "sequentialstepsedagrun", Namespace: SampleDefaultInputs.Namespace,
			}}

			result, err := reconciler.Reconcile(ctx, request)
			Expect(err).ToNot(HaveOccurred())
			Expect(result.Requeue).To(BeFalse())

			job1 := new(batchv1.Job)
			job2 := new(batchv1.Job)
			expectedjob1name := "sequentialstepsedagrun-step1"
			expectedjob2name := "sequentialstepsedagrun-step2"

			Expect(k8sClient.Get(
				ctx,
				types.NamespacedName{
					Name: expectedjob1name, Namespace: SampleDefaultInputs.Namespace,
				},
				job1,
			)).To(Succeed())
			compareJobWithEdagStep(*sequentialstepsedag, "step1", *job1)

			// Re-reconcile
			result, err = reconciler.Reconcile(ctx, request)
			Expect(err).ToNot(HaveOccurred())
			Expect(result.Requeue).To(BeFalse())

			Expect(k8sClient.Get(
				ctx,
				types.NamespacedName{
					Name: expectedjob2name, Namespace: SampleDefaultInputs.Namespace,
				},
				job2,
			)).To(Succeed())
			compareJobWithEdagStep(*sequentialstepsedag, "step2", *job2)
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
