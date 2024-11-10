package service_test

import (
	"testing"

	service "github.com/benhutchings1/kickplate/internal/service"
	"github.com/go-logr/logr"
)

func TestCreateJob(t *testing.T) {
	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient.ClientImp,
		Log:    &newLog,
	}
}

func TestStartNewJobs(t *testing.T) {

}

func TestCheckRunOwnerReference(t *testing.T) {

}

func TestIsRunComplete(t *testing.T) {

}

func TestFetchEDAG(t *testing.T) {

}
func TestFetchEDAGRun(t *testing.T) {

}

func TestIsJobComplete(t *testing.T) {

}
