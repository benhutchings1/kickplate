package builders

import (
	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

type DeploymentBuilder struct {
	Name      string
	Namespace string
	Replicas  int32
	Labels    map[string]string
	Image     string
	Port      int32
}

func (db *DeploymentBuilder) BuildDeployment() *appsv1.Deployment {
	return &appsv1.Deployment{
		ObjectMeta: metav1.ObjectMeta{
			Name:      db.Name,
			Namespace: db.Namespace,
		},
		Spec: appsv1.DeploymentSpec{
			Replicas: &db.Replicas,
			Selector: &metav1.LabelSelector{
				MatchLabels: db.Labels,
			},
			Template: corev1.PodTemplateSpec{
				ObjectMeta: metav1.ObjectMeta{
					Labels: db.Labels,
				},
				Spec: corev1.PodSpec{
					Containers: []corev1.Container{{
						Name:            db.Name,
						Image:           db.Image,
						ImagePullPolicy: corev1.PullIfNotPresent,
						Ports: []corev1.ContainerPort{{
							ContainerPort: db.Port,
							Name:          db.Name,
						}},
					},
					}},
			},
		},
	}
}

// apiVersion: apps/v1
// kind: Deployment
// metadata:
//   name: nginx-deployment
//   namespace: nginx-demo  # Optional, remove if not using a namespace
// spec:
//   replicas: 3  # Number of NGINX Pods to run
//   selector:
//     matchLabels:
//       app: nginx
//   template:
//     metadata:
//       labels:
//         app: nginx
//     spec:
//       containers:
//       - name: nginx
//         image: nginx:latest  # NGINX image
//         ports:
//         - containerPort: 80  # Port NGINX listens on
