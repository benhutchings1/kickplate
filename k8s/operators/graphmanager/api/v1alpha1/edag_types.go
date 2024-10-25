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

package v1alpha1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

type EDAGSpec struct {
	Steps []EDAGStep `json:"steps,omitempty"`
}

type EDAGStep struct {
	// +kubebuilder:validation:MaxLength=40
	Name  string `json:"name"`
	Image string `json:"image"`
	// +kubebuilder:default=1
	// +kubebuilder:validation:Maximum=10
	Replicas     int32             `json:"replicas,omitempty"`
	Dependencies []string          `json:"dependencies,omitempty"`
	Envs         map[string]string `json:"envs,omitempty"`
	Args         []string          `json:"argument,omitempty"`
	Command      []string          `json:"command,omitempty"`
}

// +kubebuilder:object:root=true
// EDAG is the Schema for the edags API
type EDAG struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec EDAGSpec `json:"spec,omitempty"`
}

//+kubebuilder:object:root=true

// EDAGList contains a list of EDAG
type EDAGList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []EDAG `json:"items"`
}

func init() {
	SchemeBuilder.Register(&EDAG{}, &EDAGList{})
}
