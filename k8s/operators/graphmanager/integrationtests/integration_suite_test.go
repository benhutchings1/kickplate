package integrationtests_test

import (
	"context"
	"fmt"
	"path/filepath"
	"runtime"
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	batchv1 "k8s.io/api/batch/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes/scheme"
	"k8s.io/client-go/rest"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/envtest"
	logf "sigs.k8s.io/controller-runtime/pkg/log"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	"github.com/benhutchings1/kickplate/builders"
)

var cfg *rest.Config
var k8sClient client.Client
var testEnv *envtest.Environment
var SampleDefaultInputs DefaultInputs
var SampleJobs []*JobContainer
var SampleEdagRun graphv1alpha1.EDAGRun
var SampleEdag graphv1alpha1.EDAG
var ctx context.Context

type DefaultInputs struct {
	DefaultLabels map[string]string
	Port          int32
	Envs          map[string]string
	Indexed       batchv1.CompletionMode
	RestartPolicy corev1.RestartPolicy
	UUID          int64
	Namespace     string
}

type JobContainer struct {
	Build *builders.JobBuilder
	Job   batchv1.Job
}

func TestControllers(t *testing.T) {
	RegisterFailHandler(Fail)

	RunSpecs(t, "Controller Suite")
}

var _ = AfterSuite(func() {
	By("tearing down the test environment")
	err := testEnv.Stop()
	Expect(err).NotTo(HaveOccurred())
})

var _ = BeforeSuite(func() {
	logf.SetLogger(zap.New(zap.WriteTo(GinkgoWriter), zap.UseDevMode(true)))

	By("creating context")
	ctx = context.Background()

	By("bootstrapping test environment")
	testEnv = &envtest.Environment{
		CRDDirectoryPaths:     []string{filepath.Join("..", "config", "crd", "bases")},
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

	By("creating testing namespace")
	newNamespaceName := "testnamespace"
	newNamespace := &corev1.Namespace{ObjectMeta: metav1.ObjectMeta{
		Name: newNamespaceName,
	}}
	Expect(k8sClient.Create(ctx, newNamespace)).ToNot(HaveOccurred())

	By("creating sample data")
	SampleDefaultInputs = DefaultInputs{
		DefaultLabels: map[string]string{
			"app": "testapp",
		},
		Port: 5000,
		Envs: map[string]string{
			"env1": "myenvvalue",
		},
		Indexed:       batchv1.IndexedCompletion,
		RestartPolicy: corev1.RestartPolicyNever,
		UUID:          2000,
		Namespace:     newNamespaceName,
	}
	edagName := "sampleedag"
	edagrunName := "sampleedagrun"
	stepnames := []string{"step1", "step2"}

	formattedEnvs := []corev1.EnvVar{}
	for key, value := range SampleDefaultInputs.Envs {
		formattedEnvs = append(
			formattedEnvs,
			corev1.EnvVar{Name: key, Value: value},
		)
	}

	By("creating sample job 1")
	jobonebuild := builders.JobBuilder{
		Name:          fmt.Sprintf("%s-%s", edagName, stepnames[0]),
		Namespace:     SampleDefaultInputs.Namespace,
		Labels:        SampleDefaultInputs.DefaultLabels,
		Image:         "testimage1:latest",
		Port:          SampleDefaultInputs.Port,
		Completions:   3,
		Paralellism:   3,
		Indexed:       SampleDefaultInputs.Indexed,
		RestartPolicy: SampleDefaultInputs.RestartPolicy,
		Command:       []string{"cmd", "arg"},
		UserUUID:      SampleDefaultInputs.UUID,
		Envs:          formattedEnvs,
	}
	jobone := JobContainer{
		Build: &jobonebuild,
		Job:   *jobonebuild.BuildJob(),
	}
	SampleJobs = append(SampleJobs, &jobone)

	By("creating sample job 2")
	jobtwobuild := builders.JobBuilder{
		Name:          fmt.Sprintf("%s-%s", edagName, stepnames[1]),
		Namespace:     SampleDefaultInputs.Namespace,
		Labels:        SampleDefaultInputs.DefaultLabels,
		Image:         "testimage2:latest",
		Port:          SampleDefaultInputs.Port,
		Completions:   2,
		Paralellism:   2,
		Indexed:       SampleDefaultInputs.Indexed,
		RestartPolicy: SampleDefaultInputs.RestartPolicy,
		Command:       []string{"cli", "anotherarg"},
		UserUUID:      SampleDefaultInputs.UUID,
		Envs:          formattedEnvs,
	}

	jobtwo := JobContainer{
		Build: &jobtwobuild,
		Job:   *jobtwobuild.BuildJob(),
	}
	SampleJobs = append(SampleJobs, &jobtwo)

	By("creating sample edag")
	SampleEdag = graphv1alpha1.EDAG{
		TypeMeta: metav1.TypeMeta{
			Kind:       "EDAG",
			APIVersion: "edag.kickplate.com/v1alpha1",
		},
		ObjectMeta: metav1.ObjectMeta{
			Name:      edagName,
			Namespace: SampleDefaultInputs.Namespace,
		},
		Spec: graphv1alpha1.EDAGSpec{
			Steps: map[string]graphv1alpha1.EDAGStep{
				stepnames[0]: {
					Image:    jobonebuild.Image,
					Replicas: jobonebuild.Completions,
					Envs:     SampleDefaultInputs.Envs,
					Args:     jobonebuild.Command,
				},
				stepnames[1]: {
					Image:    jobtwobuild.Image,
					Replicas: jobtwobuild.Completions,
					Envs:     SampleDefaultInputs.Envs,
					Args:     jobtwobuild.Command,
				},
			},
		},
	}

	By("creating sample run")
	SampleEdagRun = graphv1alpha1.EDAGRun{
		ObjectMeta: metav1.ObjectMeta{
			Namespace: SampleDefaultInputs.Namespace,
			Name:      edagrunName,
		},
		Spec: graphv1alpha1.EDAGRunSpec{
			EDAGName: edagName,
		},
	}
})
