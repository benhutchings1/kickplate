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

type EDAGRunSpec struct {
	Graph EDAG `json:"edag"`
}

type EDAGRunStatus struct {
	Conditions []metav1.Condition `json:"conditions,omitempty" patchStrategy:"merge" patchMergeKey:"type" protobuf:"bytes,1,rep,name=conditions"`
}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status

// EDAGRun is the Schema for the edagruns API
type EDAGRun struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   EDAGRunSpec   `json:"spec,omitempty"`
	Status EDAGRunStatus `json:"status,omitempty"`
}

//+kubebuilder:object:root=true

// EDAGRunList contains a list of EDAGRun
type EDAGRunList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []EDAGRun `json:"items"`
}

func init() {
	SchemeBuilder.Register(&EDAGRun{}, &EDAGRunList{})
}
