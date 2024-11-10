package service_test

import (
	"context"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	clusterclient "github.com/benhutchings1/kickplate/internal/clusterclient"
	"github.com/stretchr/testify/mock"
	batchv1 "k8s.io/api/batch/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	"sigs.k8s.io/controller-runtime/pkg/client"
)

type MockEDAGRunClient struct {
	*clusterclient.ClientImp
	mock.Mock
}

func (c *MockEDAGRunClient) CreateJob(ctx context.Context, job *batchv1.Job) error {
	args := c.Called(ctx, job)
	return args.Error(0)
}

func (c *MockEDAGRunClient) FetchResource(
	ctx context.Context,
	key types.NamespacedName,
	obj client.Object,
) error {
	args := c.Called(ctx, key, obj)
	return args.Error(0)
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
	parentObj client.Object,
	childObj client.Object,
) error {
	args := c.Called(parentObj, childObj)
	return args.Error(0)
}
