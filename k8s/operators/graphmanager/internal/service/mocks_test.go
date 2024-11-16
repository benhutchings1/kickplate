package service_test

import (
	"context"
	"fmt"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	"github.com/benhutchings1/kickplate/builders"
	clusterclient "github.com/benhutchings1/kickplate/internal/clusterclient"
	"github.com/benhutchings1/kickplate/internal/service"
	"github.com/stretchr/testify/mock"
	batchv1 "k8s.io/api/batch/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	"sigs.k8s.io/controller-runtime/pkg/client"
)

type MockEDAGRunClient struct {
	mock.Mock
	clusterclient.ClusterClientManager
}

func (c *MockEDAGRunClient) CreateJob(ctx context.Context, obj client.Object) error {
	args := c.Called(ctx, obj)
	return args.Error(0)
}

func (c *MockEDAGRunClient) FetchResource(
	ctx context.Context,
	key types.NamespacedName,
	obj client.Object,
) (isfound bool, err error) {
	args := c.Called(ctx, key, obj)
	return args.Bool(0), args.Error(1)
}

func (c *MockEDAGRunClient) UpdateResource(
	ctx context.Context,
	obj client.Object,
) error {
	args := c.Called(ctx, obj)
	return args.Error(0)
}

func (c *MockEDAGRunClient) UpdateStatus(
	ctx context.Context,
	run *graphv1alpha1.EDAGRun,
	newCondition metav1.Condition,
) error {
	args := c.Called(ctx, run, newCondition)
	return args.Error(0)
}

func (c *MockEDAGRunClient) SetControllerReference(
	ctx context.Context,
	parentObj client.Object,
	childObj client.Object,
) error {
	args := c.Called(ctx, parentObj, childObj)
	return args.Error(0)
}

type JobDesc struct {
	Name         string
	Image        string
	Replicas     int32
	Command      []string
	Envs         []corev1.EnvVar
	Stepname     string
	Dependencies []string
}

type Inputs struct {
	DefaultLabels map[string]string
	Port          int32
	Envs          map[string]string
	Indexed       batchv1.CompletionMode
	RestartPolicy corev1.RestartPolicy
	UUID          int64
	Namespace     string
	EDAGRunName   string
	EDAGName      string
	Jobs          []JobDesc
}

func SampleInputsFactory() Inputs {
	return Inputs{
		Port: 5000,
		DefaultLabels: map[string]string{
			"env1": "value1",
		},
		Indexed:       batchv1.IndexedCompletion,
		RestartPolicy: corev1.RestartPolicyAlways,
		UUID:          3000,
		Namespace:     "samplenamespace",
		EDAGRunName:   "sampleedagrunname",
		EDAGName:      "sampleedagname",
		Jobs: []JobDesc{
			{
				Name:         "sampleedagrunname-job1",
				Stepname:     "job1",
				Image:        "jobimage1",
				Replicas:     12,
				Command:      []string{"command", "thing"},
				Envs:         []corev1.EnvVar{{Name: "name1", Value: "value1"}},
				Dependencies: []string{},
			},
			{
				Name:         "sampleedagrunname-job2",
				Stepname:     "job2",
				Image:        "jobimage2",
				Replicas:     12,
				Command:      []string{"command", "thing"},
				Envs:         []corev1.EnvVar{{Name: "name1", Value: "value1"}},
				Dependencies: []string{"job1"},
			},
		},
	}
}

func SampleEDAGRunFactory(inp Inputs) graphv1alpha1.EDAGRun {
	return graphv1alpha1.EDAGRun{
		ObjectMeta: metav1.ObjectMeta{
			Name:      inp.EDAGRunName,
			Namespace: inp.Namespace,
		},
		Spec: graphv1alpha1.EDAGRunSpec{
			EDAGName: inp.EDAGName,
		},
		Status: graphv1alpha1.EDAGRunStatus{
			Conditions: []metav1.Condition{
				{Type: string(service.RunInProgress), Status: metav1.ConditionTrue},
			},
		},
	}
}

func SampleEDAGFactory(inp Inputs) graphv1alpha1.EDAG {
	steps := map[string]graphv1alpha1.EDAGStep{}

	for _, job := range inp.Jobs {
		envs := map[string]string{}
		for _, env := range job.Envs {
			envs[env.Name] = env.Value
		}

		steps[job.Stepname] = graphv1alpha1.EDAGStep{
			Image:        job.Image,
			Replicas:     job.Replicas,
			Envs:         envs,
			Args:         job.Command,
			Dependencies: job.Dependencies,
		}
	}

	return graphv1alpha1.EDAG{
		TypeMeta: metav1.TypeMeta{
			Kind:       "EDAG",
			APIVersion: "edag.kickplate.com/v1alpha1",
		},
		ObjectMeta: metav1.ObjectMeta{
			Name:      inp.EDAGName,
			Namespace: inp.Namespace,
		},
		Spec: graphv1alpha1.EDAGSpec{
			Steps: steps,
		},
	}
}

func SampleJobFactory(job JobDesc, inp Inputs) *batchv1.Job {
	builder := builders.JobBuilder{
		Name:          job.Name,
		Namespace:     inp.Namespace,
		Labels:        inp.DefaultLabels,
		Image:         job.Image,
		Port:          inp.Port,
		Completions:   job.Replicas,
		Paralellism:   job.Replicas,
		Indexed:       batchv1.IndexedCompletion,
		RestartPolicy: corev1.RestartPolicyNever,
		Command:       job.Command,
		UserUUID:      inp.UUID,
		Envs:          job.Envs,
	}
	return builder.BuildJob()
}

func SampleDataFactory() (
	inputs Inputs,
	edag graphv1alpha1.EDAG,
	edagrun graphv1alpha1.EDAGRun,
) {
	inputs = SampleInputsFactory()

	jobDescs := []JobDesc{
		{
			Name:     fmt.Sprintf("%s-%s", inputs.EDAGRunName, "step1"),
			Image:    "step1image",
			Replicas: 32,
			Command:  []string{"cmd", "step1"},
			Envs: []corev1.EnvVar{
				{Name: "step1", Value: "value1"},
			},
			Stepname:     "step1",
			Dependencies: []string{},
		},
		{
			Name:     fmt.Sprintf("%s-%s", inputs.EDAGRunName, "step2"),
			Image:    "step2image",
			Replicas: 14,
			Command:  []string{"cmd", "step2"},
			Envs: []corev1.EnvVar{
				{Name: "step2", Value: "value2"},
			},
			Stepname:     "step2",
			Dependencies: []string{"step1"},
		},
		{
			Name:     fmt.Sprintf("%s-%s", inputs.EDAGRunName, "step3"),
			Image:    "step3image",
			Replicas: 83,
			Command:  []string{"cmd", "step3"},
			Envs: []corev1.EnvVar{
				{Name: "step3", Value: "value3"},
			},
			Stepname:     "step3",
			Dependencies: []string{},
		},
		{
			Name:     fmt.Sprintf("%s-%s", inputs.EDAGRunName, "step4"),
			Image:    "step4image",
			Replicas: 73,
			Command:  []string{"cmd", "step4"},
			Envs: []corev1.EnvVar{
				{Name: "step4", Value: "value4"},
			},
			Stepname:     "step4",
			Dependencies: []string{"step3"},
		},
		{
			Name:     fmt.Sprintf("%s-%s", inputs.EDAGRunName, "step5"),
			Image:    "step5image",
			Replicas: 992,
			Command:  []string{"cmd", "step5"},
			Envs: []corev1.EnvVar{
				{Name: "step5", Value: "value5"},
			},
			Stepname:     "step5",
			Dependencies: []string{"step4", "step1"},
		},
	}
	inputs.Jobs = jobDescs

	edag = SampleEDAGFactory(inputs)
	edagrun = SampleEDAGRunFactory(inputs)

	edagrun.Status.Jobs = map[string]string{}
	for _, job := range inputs.Jobs {
		edagrun.Status.Jobs[job.Stepname] = job.Name
	}

	return
}
