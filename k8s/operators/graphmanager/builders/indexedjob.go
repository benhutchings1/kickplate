package builders

import (
	batchv1 "k8s.io/api/batch/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

type JobBuilder struct {
	Name          string
	Image         string
	Namespace     string
	Labels        map[string]string
	Completions   int32
	Paralellism   int32
	Indexed       batchv1.CompletionMode
	RestartPolicy corev1.RestartPolicy
	Command       []string
	UserUUID      int64
	Port          int32
	Envs          []corev1.EnvVar
}

func (JobInputs *JobBuilder) BuildJob() *batchv1.Job {
	return &batchv1.Job{
		ObjectMeta: metav1.ObjectMeta{
			Name:      JobInputs.Name,
			Namespace: JobInputs.Namespace,
		},
		Spec: batchv1.JobSpec{
			Completions:    &JobInputs.Completions,
			Parallelism:    &JobInputs.Paralellism,
			CompletionMode: &JobInputs.Indexed,
			Template: corev1.PodTemplateSpec{
				Spec: corev1.PodSpec{
					RestartPolicy: JobInputs.RestartPolicy,
					Containers: []corev1.Container{
						{
							Image:           JobInputs.Image,
							Name:            JobInputs.Name,
							ImagePullPolicy: corev1.PullIfNotPresent,
							Command:         JobInputs.Command,
							SecurityContext: &corev1.SecurityContext{
								RunAsNonRoot:             &[]bool{true}[0],
								RunAsUser:                &[]int64{JobInputs.UserUUID}[0],
								AllowPrivilegeEscalation: &[]bool{false}[0],
								Capabilities: &corev1.Capabilities{
									Drop: []corev1.Capability{
										"ALL",
									},
								},
							},
							Ports: []corev1.ContainerPort{
								{
									ContainerPort: JobInputs.Port,
									Name:          "jobport",
								},
							},
							Env: JobInputs.Envs,
						},
					},
				},
			},
		},
	}
}
