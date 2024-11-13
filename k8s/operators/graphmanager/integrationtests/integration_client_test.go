package integrationtests_test

import (
	"context"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	"github.com/benhutchings1/kickplate/builders"
	client "github.com/benhutchings1/kickplate/internal/clusterclient"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	batchv1 "k8s.io/api/batch/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/client-go/kubernetes/scheme"
	logf "sigs.k8s.io/controller-runtime/pkg/log"
)

var clusterclient client.ClusterClient

var _ = Describe("EDAGRun Cluster Client", func() {
	ctx := context.Background()

	BeforeEach(func() {
		By("instansiating cluster client")
		clusterclient = client.ClusterClient{
			K8sClient: k8sClient,
			Scheme:    scheme.Scheme,
			Log:       &logf.Log,
		}
	})

	Context("when fetching a resource", func() {
		It("should fetch existing EDAGRun", func() {
			fetchedRun := &graphv1alpha1.EDAGRun{}
			err, found := clusterclient.FetchResource(ctx, types.NamespacedName{
				Name:      "sampleedagrun",
				Namespace: SampleDefaultInputs.Namespace,
			}, fetchedRun)
			Expect(err).To(Succeed())
			Expect(found).To(BeTrue())
		})
		It("should return error on existing kind but not found instance", func() {
			fetchedEdag := &graphv1alpha1.EDAG{}
			err, found := clusterclient.FetchResource(ctx, types.NamespacedName{
				Name:      "somerandomthing",
				Namespace: SampleDefaultInputs.Namespace,
			}, fetchedEdag)
			Expect(err).To(HaveOccurred())
			Expect(found).To(BeFalse())
		})
	})
	Context("when updating a resource", func() {
		It("should update run details", func() {
			edagrunNameToUpdate := "edagruntoupdate"
			oldedagName := "edagbeforeupdate"
			newedagname := "edagafterupdate"
			edagrunToUpdate := graphv1alpha1.EDAGRun{
				ObjectMeta: metav1.ObjectMeta{
					Namespace: SampleDefaultInputs.Namespace,
					Name:      edagrunNameToUpdate,
				},
				Spec: graphv1alpha1.EDAGRunSpec{
					EDAGName: oldedagName,
				},
			}
			Expect(k8sClient.Create(ctx, &edagrunToUpdate)).To(Succeed())

			fetchedRun := &graphv1alpha1.EDAGRun{}
			Expect(k8sClient.Get(ctx, types.NamespacedName{
				Name:      "sampleedagrun",
				Namespace: SampleDefaultInputs.Namespace,
			}, fetchedRun)).ToNot(HaveOccurred())
			fetchedRun.Spec.EDAGName = newedagname

			Expect(clusterclient.UpdateResources(ctx, fetchedRun)).To(Succeed())
			Expect(fetchedRun.Spec.EDAGName).Should(Equal(newedagname))

		})
	})
	Context("when updating a resource's status", func() {
		It("should update run status", func() {
			run := &graphv1alpha1.EDAGRun{}

			Expect(k8sClient.Get(ctx, types.NamespacedName{
				Name:      "sampleedagrun",
				Namespace: SampleDefaultInputs.Namespace,
			}, run)).ToNot(HaveOccurred())

			run.Status.Jobs = map[string]string{
				"step1": "step1jobname",
			}
			newCondition := metav1.Condition{
				Type: "InProgress", Status: metav1.ConditionTrue,
				Reason: "JobStart", Message: "new condition reason",
			}
			Expect(clusterclient.UpdateStatus(ctx, run, newCondition)).To(Succeed())

			fetchedRun := &graphv1alpha1.EDAGRun{}
			Expect(k8sClient.Get(ctx, types.NamespacedName{
				Name:      "sampleedagrun",
				Namespace: SampleDefaultInputs.Namespace,
			}, fetchedRun)).To(Succeed())
			fetchedCondition := fetchedRun.Status.Conditions[0]

			Expect(fetchedCondition.Type).Should(Equal(newCondition.Type))
			Expect(fetchedCondition.Status).Should(Equal(newCondition.Status))
			Expect(fetchedCondition.Reason).Should(Equal(newCondition.Reason))
			Expect(fetchedCondition.Message).Should(Equal(newCondition.Message))
		})
	})
	Context("when creating a job", func() {
		It("should create new job", func() {
			newJobName := "mynewjob"
			newJobBuilder := builders.JobBuilder{
				Name:      newJobName,
				Image:     "newimage",
				Namespace: SampleDefaultInputs.Namespace,
				Labels: map[string]string{
					"label1": "value1",
				},
				Completions:   2,
				Paralellism:   2,
				Indexed:       batchv1.NonIndexedCompletion,
				RestartPolicy: corev1.RestartPolicyNever,
				Command:       []string{"one", "two"},
				UserUUID:      100,
				Port:          int32(200),
				Envs: []corev1.EnvVar{
					{Name: "env1", Value: "value1"},
				},
			}
			Expect(clusterclient.CreateJob(ctx, newJobBuilder.BuildJob())).To(Succeed())
			fetchedJob := &batchv1.Job{}
			Expect(k8sClient.Get(ctx, types.NamespacedName{
				Namespace: SampleDefaultInputs.Namespace,
				Name:      newJobName,
			}, fetchedJob)).To(Succeed())
		})
	})
	Context("when setting a controller reference", func() {
		It("should set reference on parent resource to child resource", func() {
			parent := &graphv1alpha1.EDAG{}
			child := &graphv1alpha1.EDAGRun{}

			Expect(k8sClient.Get(ctx, types.NamespacedName{
				Namespace: SampleDefaultInputs.Namespace,
				Name:      "sampleedag",
			}, parent)).To(Succeed())

			Expect(k8sClient.Get(ctx, types.NamespacedName{
				Namespace: SampleDefaultInputs.Namespace,
				Name:      "sampleedagrun",
			}, child)).To(Succeed())

			Expect(clusterclient.SetControllerReference(
				ctx, parent, child,
			)).To(Succeed())

			// Repull to reflect update to reference
			Expect(k8sClient.Get(ctx, types.NamespacedName{
				Namespace: SampleDefaultInputs.Namespace,
				Name:      "sampleedag",
			}, parent)).To(Succeed())

			Expect(k8sClient.Get(ctx, types.NamespacedName{
				Namespace: SampleDefaultInputs.Namespace,
				Name:      "sampleedagrun",
			}, child)).To(Succeed())

			found := false
			for _, ownerRef := range child.GetOwnerReferences() {
				if ownerRef.Kind == "EDAGRun" {
					found = true
				}
			}
			Expect(found).To(BeTrue())
		})
	})
})
