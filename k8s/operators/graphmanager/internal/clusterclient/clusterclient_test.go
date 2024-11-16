package clusterclient_test

import (
	"context"
	"errors"
	"testing"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	"github.com/benhutchings1/kickplate/internal/clusterclient"
	"github.com/go-logr/logr"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	v1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
)

func TestFetchResource(t *testing.T) {
	newLog := logr.Discard()
	newMockScheme := NewMockScheme()
	mockK8sClient := MockK8sClient{}

	client := clusterclient.ClusterClient{
		K8sClient: &mockK8sClient,
		Scheme:    newMockScheme.Scheme,
		Log:       &newLog,
	}
	key := types.NamespacedName{
		Name:      "testname",
		Namespace: "testnamespace",
	}
	obj := graphv1alpha1.EDAG{}

	mockK8sClient.On("Get", context.TODO(), key, &obj, mock.Anything).Return(
		nil,
	).Times(1)

	found, err := client.FetchResource(context.TODO(), key, &obj)

	assert.NoError(t, err)
	assert.True(t, found)
}

func TestFetchResourceFailedNotFoundShouldReturnError(t *testing.T) {
	err := errors.New("Object not found")

	clusterclient.IsNotFoundFn = func(passedErr error) bool {
		assert.Equal(t, passedErr, err)
		return false
	}

	newLog := logr.Discard()
	newMockScheme := NewMockScheme()
	mockK8sClient := MockK8sClient{}

	client := clusterclient.ClusterClient{
		K8sClient: &mockK8sClient,
		Scheme:    newMockScheme.Scheme,
		Log:       &newLog,
	}
	key := types.NamespacedName{
		Name:      "testname",
		Namespace: "testnamespace",
	}
	obj := graphv1alpha1.EDAG{}

	mockK8sClient.On("Get", context.TODO(), key, &obj, mock.Anything).Return(
		err,
	)

	found, rtnErr := client.FetchResource(context.TODO(), key, &obj)

	assert.NoError(t, rtnErr)
	assert.False(t, found)
}

func TestFetchResourceFailedFoundShouldReturnError(t *testing.T) {
	err := errors.New("Object was found with an error")

	clusterclient.IsNotFoundFn = func(passedErr error) bool {
		assert.Equal(t, passedErr, err)
		return true
	}

	newLog := logr.Discard()
	newMockScheme := NewMockScheme()
	mockK8sClient := MockK8sClient{}

	client := clusterclient.ClusterClient{
		K8sClient: &mockK8sClient,
		Scheme:    newMockScheme.Scheme,
		Log:       &newLog,
	}
	key := types.NamespacedName{
		Name:      "testname",
		Namespace: "testnamespace",
	}
	obj := graphv1alpha1.EDAG{}

	mockK8sClient.On("Get", context.TODO(), key, &obj, mock.Anything).Return(
		err,
	)

	found, rtnErr := client.FetchResource(context.TODO(), key, &obj)

	assert.Error(t, rtnErr)
	assert.False(t, found)
}

func TestUpdateResource(t *testing.T) {
	newLog := logr.Discard()
	newMockScheme := NewMockScheme()
	mockK8sClient := MockK8sClient{}

	client := clusterclient.ClusterClient{
		K8sClient: &mockK8sClient,
		Scheme:    newMockScheme.Scheme,
		Log:       &newLog,
	}

	obj := graphv1alpha1.EDAG{}

	mockK8sClient.On("Update", context.TODO(), mock.AnythingOfType("*v1alpha1.EDAG"), mock.Anything).Return(
		nil,
	).Times(1)
	rtnErr := client.UpdateResources(context.TODO(), &obj)

	assert.NoError(t, rtnErr)
}

func TestUpdateResourceShouldReturnError(t *testing.T) {
	err := errors.New("Failure to update")

	newLog := logr.Discard()
	newMockScheme := NewMockScheme()
	mockK8sClient := MockK8sClient{}

	client := clusterclient.ClusterClient{
		K8sClient: &mockK8sClient,
		Scheme:    newMockScheme.Scheme,
		Log:       &newLog,
	}
	obj := graphv1alpha1.EDAG{}

	mockK8sClient.On("Update", context.TODO(), mock.AnythingOfType("*v1alpha1.EDAG"), mock.Anything).Return(
		err,
	).Times(1)
	rtnErr := client.UpdateResources(context.TODO(), &obj)

	assert.Error(t, rtnErr)
}

func TestUpdateStatus(t *testing.T) {
	newLog := logr.Discard()
	newMockScheme := NewMockScheme()
	mockK8sClient := MockK8sClient{}

	client := clusterclient.ClusterClient{
		K8sClient: &mockK8sClient,
		Scheme:    newMockScheme.Scheme,
		Log:       &newLog,
	}
	obj := graphv1alpha1.EDAGRun{}
	obj.Name = "TestName"
	obj.Status.Conditions = []metav1.Condition{}

	newCondition := metav1.Condition{
		Type: "Unsafe", Status: metav1.ConditionFalse,
	}

	mockedSubResourceWriter := MockSubResourceWriter{}

	mockK8sClient.On("Status").Return(&mockedSubResourceWriter)
	mockedSubResourceWriter.On("Update", context.TODO(), mock.AnythingOfType("*v1alpha1.EDAGRun")).Return(
		nil,
	).Times(1)

	rtnErr := client.UpdateStatus(context.TODO(), &obj, newCondition)

	assert.NoError(t, rtnErr)
}

func TestUpdateStatusShouldReturnError(t *testing.T) {
	err := errors.New("Failure to update")
	newLog := logr.Discard()
	newMockScheme := NewMockScheme()
	mockK8sClient := MockK8sClient{}

	client := clusterclient.ClusterClient{
		K8sClient: &mockK8sClient,
		Scheme:    newMockScheme.Scheme,
		Log:       &newLog,
	}
	obj := graphv1alpha1.EDAGRun{}
	obj.Name = "TestName"
	obj.Status.Conditions = []metav1.Condition{}

	newCondition := metav1.Condition{
		Type: "Unsafe", Status: metav1.ConditionFalse,
	}

	mockedSubResourceWriter := MockSubResourceWriter{}

	mockK8sClient.On("Status").Return(&mockedSubResourceWriter)
	mockedSubResourceWriter.On("Update", context.TODO(), mock.AnythingOfType("*v1alpha1.EDAGRun")).Return(
		err,
	).Times(1)

	rtnErr := client.UpdateStatus(context.TODO(), &obj, newCondition)

	assert.Error(t, rtnErr, err)
}

func TestSetControllerReference(t *testing.T) {
	newLog := logr.Discard()
	newMockScheme := NewMockScheme()
	mockK8sClient := MockK8sClient{}

	client := clusterclient.ClusterClient{
		K8sClient: &mockK8sClient,
		Scheme:    newMockScheme.Scheme,
		Log:       &newLog,
	}
	edag := graphv1alpha1.EDAG{}
	run := graphv1alpha1.EDAGRun{}

	clusterclient.SetControllerReferenceFn = func(
		owner v1.Object,
		controlled v1.Object,
		scheme *runtime.Scheme,
		opts ...controllerutil.OwnerReferenceOption,
	) error {
		edagOwner, ok := owner.(*graphv1alpha1.EDAGRun)
		assert.True(t, ok)
		assert.Equal(t, edagOwner, &run)

		runControlled, ok := controlled.(*graphv1alpha1.EDAG)
		assert.True(t, ok)
		assert.Equal(t, runControlled, &edag)

		return nil
	}

	mockK8sClient.On("Update", context.TODO(), mock.AnythingOfType("*v1alpha1.EDAG"), mock.Anything).Return(
		nil,
	).Times(1)

	err := client.SetControllerReference(context.TODO(), &edag, &run)

	assert.NoError(t, err)
}

func TestSetControllerReferenceFailedOnSameObject(t *testing.T) {
	newLog := logr.Discard()
	newMockScheme := NewMockScheme()
	mockK8sClient := MockK8sClient{}

	client := clusterclient.ClusterClient{
		K8sClient: &mockK8sClient,
		Scheme:    newMockScheme.Scheme,
		Log:       &newLog,
	}
	edag := graphv1alpha1.EDAG{}

	err := client.SetControllerReference(context.TODO(), &edag, &edag)

	assert.Error(t, err)
}
