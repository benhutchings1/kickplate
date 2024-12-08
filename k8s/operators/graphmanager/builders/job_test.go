package builders_test

import (
	"testing"

	builder "github.com/benhutchings1/kickplate/builders"
	"github.com/go-test/deep"
	batchv1 "k8s.io/api/batch/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

func TestJobBuilder(t *testing.T) {
	jobBuilder := builder.JobBuilder{
		Name:      "jb",
		Image:     "testimage",
		Namespace: "testnsp",
		Labels: map[string]string{
			"app": "testapp",
		},
		Completions:   3,
		Paralellism:   3,
		Indexed:       batchv1.IndexedCompletion,
		RestartPolicy: corev1.RestartPolicyNever,
		Command:       []string{"start", "app"},
		Args:          []string{"run", "env"},
		UserUUID:      100,
		Port:          2000,
		Envs: []corev1.EnvVar{
			{Name: "env1", Value: "value1"},
		},
	}
	expectedParalellism := int32(3)
	expectedCompletion := batchv1.IndexedCompletion
	expectedResponse := &batchv1.Job{
		ObjectMeta: metav1.ObjectMeta{
			Name:      "jb",
			Namespace: "testnsp",
		},
		Spec: batchv1.JobSpec{
			Completions:    &expectedParalellism,
			Parallelism:    &expectedParalellism,
			CompletionMode: &expectedCompletion,
			Template: corev1.PodTemplateSpec{
				Spec: corev1.PodSpec{
					RestartPolicy: corev1.RestartPolicyNever,
					Containers: []corev1.Container{
						{
							Image:           "testimage",
							Name:            "jb",
							ImagePullPolicy: corev1.PullIfNotPresent,
							Command:         []string{"start", "app"},
							Args:            []string{"run", "env"},
							SecurityContext: &corev1.SecurityContext{
								RunAsNonRoot:             &[]bool{true}[0],
								RunAsUser:                &[]int64{100}[0],
								AllowPrivilegeEscalation: &[]bool{false}[0],
								Capabilities: &corev1.Capabilities{
									Drop: []corev1.Capability{
										"ALL",
									},
								},
							},
							Ports: []corev1.ContainerPort{
								{
									ContainerPort: 2000,
									Name:          "jobport",
								},
							},
							Env: []corev1.EnvVar{
								{Name: "env1", Value: "value1"},
							},
						},
					},
				},
			},
		},
	}
	generatedJob := jobBuilder.BuildJob()
	diff := deep.Equal(generatedJob, expectedResponse)
	if diff != nil {
		t.Errorf("Expected jobs to be equal. diff: %v", diff)
	}
}
