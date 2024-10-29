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
	"fmt"
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"

	batchv1 "k8s.io/api/batch/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	"github.com/benhutchings1/kickplate/builders"
	//+kubebuilder:scaffold:imports
)

// These tests use Ginkgo (BDD-style Go testing framework). Refer to
// http://onsi.github.io/ginkgo/ to learn more about Ginkgo.

var SampleDefaultInputs DefaultInputs
var SampleJobs []*JobContainer
var SampleEdagRuns graphv1alpha1.EDAGRun
var SampleEdag graphv1alpha1.EDAG

func TestControllers(t *testing.T) {
	RegisterFailHandler(Fail)

	RunSpecs(t, "Controller Suite")
}

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

var _ = BeforeSuite(func() {
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
		Namespace:     "testnamespace",
	}
	edagName := "sampleedag"
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
	SampleEdagRuns = graphv1alpha1.EDAGRun{
		Spec: graphv1alpha1.EDAGRunSpec{
			EDAGName: edagName,
		},
	}

})
