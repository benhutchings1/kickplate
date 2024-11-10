package clusterclient_test

import (
	"context"

	"github.com/stretchr/testify/mock"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	"sigs.k8s.io/controller-runtime/pkg/client"
)

type MockK8sClient struct {
	mock.Mock
	client.Client
}

type MockSubResourceWriter struct {
	mock.Mock
	client.SubResourceWriter
}

func (c *MockK8sClient) Get(ctx context.Context, key types.NamespacedName, obj client.Object, opts ...client.GetOption) error {
	args := c.Called(ctx, key, obj, opts)
	return args.Error(0)
}

func (c *MockK8sClient) Update(ctx context.Context, obj client.Object, opts ...client.UpdateOption) error {
	args := c.Called(ctx, obj, opts)
	return args.Error(0)
}

func (c *MockK8sClient) Status() client.SubResourceWriter {
	args := c.Called()
	return args.Get(0).(client.SubResourceWriter)
}

func (srw *MockSubResourceWriter) Update(ctx context.Context, obj client.Object, opts ...client.SubResourceUpdateOption) error {
	args := srw.Called(ctx, obj)
	return args.Error(0)
}

type MockScheme struct {
	mock.Mock
	Scheme *runtime.Scheme
}

func NewMockScheme() MockScheme {
	return MockScheme{
		Scheme: runtime.NewScheme(),
	}
}
