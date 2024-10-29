package controller_test

import (
	"time"

	"github.com/benhutchings1/kickplate/internal/controller"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"

	batchv1 "k8s.io/api/batch/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

var JobConditions []batchv1.JobCondition

var _ = Describe("EdagService", func() {
	Context("when evaluating condition of resource", func() {
		When("there are many conditions", func() {
			BeforeEach(func() {
				JobConditions = []batchv1.JobCondition{
					{
						Type:               batchv1.JobComplete,
						Status:             corev1.ConditionTrue,
						Reason:             "Job Finished",
						Message:            "Finished",
						LastProbeTime:      metav1.Time{Time: time.Now()},
						LastTransitionTime: metav1.Time{Time: time.Now()},
					},
					{
						Type:               batchv1.JobComplete,
						Status:             corev1.ConditionTrue,
						Reason:             "Job Finished",
						Message:            "Finished",
						LastProbeTime:      metav1.Time{Time: time.Now()},
						LastTransitionTime: metav1.Time{Time: time.Now()},
					},
				}
			})
			It("extracts the last condition", func() {

			})
		})

		When("there are no conditions", func() {
			It("returns nil", func() {
				Expect(controller.IsJobComplete(&SampleJobs[0].Job)).To(BeNil())
			})
		})
	})
})
