package clusterclient_test

// import (
// 	"context"
// 	"testing"

// 	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
// 	batchv1 "k8s.io/api/batch/v1"
// 	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
// 	"k8s.io/apimachinery/pkg/types"
// 	"sigs.k8s.io/controller-runtime/pkg/client"
// )

// type MockEDAGRunClient struct {
// 	MockCreateJob     func(ctx context.Context, job *batchv1.Job) error
// 	MockFetchResource func(
// 		ctx context.Context,
// 		key types.NamespacedName,
// 		obj client.Object,
// 		LogError bool,
// 	) error
// 	MockUpdateResource func(
// 		ctx context.Context,
// 		obj client.Object,
// 	) error
// 	MockUpdateStatus func(
// 		ctx context.Context,
// 		run *graphv1alpha1.EDAGRun,
// 		newCondition metav1.Condition,
// 	) error
// 	MockSetControllerReference func(
// 		parentObj client.Object,
// 		childObj client.Object,
// 	) error
// }

// func TestCreateJob(t *testing.T) {

// }

// func TestStartNewJobs(t *testing.T) {

// }

// func TestCheckRunOwnerReference(t *testing.T) {

// }

// func TestIsRunComplete(t *testing.T) {

// }

// func TestFetchEDAG(t *testing.T) {

// }
// func TestFetchEDAGRun(t *testing.T) {

// }

// func TestIsJobComplete(t *testing.T) {

// }
