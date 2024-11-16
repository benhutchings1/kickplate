package service_test

import (
	"context"
	"errors"
	"fmt"
	"testing"

	graphv1alpha1 "github.com/benhutchings1/kickplate/api/v1alpha1"
	service "github.com/benhutchings1/kickplate/internal/service"
	"github.com/go-logr/logr"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	batchv1 "k8s.io/api/batch/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
)

func TestCreateJob(t *testing.T) {
	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient,
		Log:    &newLog,
	}
	sampleinps := SampleInputsFactory()
	edag := SampleEDAGFactory(sampleinps)
	run := SampleEDAGRunFactory(sampleinps)
	jobSpec := sampleinps.Jobs[0]

	expectedRun := run.DeepCopy()
	expectedRun.Status.Jobs = map[string]string{
		jobSpec.Name: fmt.Sprintf("%s-%s", run.Name, jobSpec.Name),
	}

	envs := map[string]string{}

	for _, env := range jobSpec.Envs {
		envs[env.Name] = env.Value
	}

	stepSpec := graphv1alpha1.EDAGStep{
		Image:        jobSpec.Image,
		Replicas:     jobSpec.Replicas,
		Dependencies: []string{},
		Envs:         envs,
		Args:         jobSpec.Command,
	}

	expectedJobName := fmt.Sprintf("%s-%s", run.Name, jobSpec.Name)

	expectedCondition := metav1.Condition{
		Type: string(service.RunInProgress), Status: metav1.ConditionTrue,
		Reason: "JobStart", Message: fmt.Sprintf("Created %s", expectedJobName),
	}

	mockedClient.On(
		"CreateJob", context.TODO(), mock.AnythingOfType("*v1.Job"),
	).Return(nil).Times(1)
	mockedClient.On(
		"UpdateStatus", context.TODO(), mock.Anything, expectedCondition,
	).Return(nil).Times(1)
	mockedClient.On(
		"SetControllerReference", expectedRun, mock.Anything,
	).Return(nil).Times(1)

	assert.NoError(t, mockedService.CreateJob(
		context.TODO(),
		&edag, &run,
		jobSpec.Name,
		stepSpec,
		sampleinps.Namespace,
		sampleinps.Port,
		sampleinps.DefaultLabels,
	))

}

func TestStartNewJobsShouldDoNothing(t *testing.T) {
	// Simulate only two steps in run
	// step2 dependent on step1
	// step1 - inprogress, step2 - not started
	// Should check step1 is active, then not start step2
	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient,
		Log:    &newLog,
	}
	sampleinps, edag, run := SampleDataFactory()

	step1 := sampleinps.Jobs[0]
	step2 := sampleinps.Jobs[1]
	step1Job := SampleJobFactory(step1, sampleinps)
	run.Status.Jobs = map[string]string{
		step1.Stepname: step1.Name,
	}
	edag.Spec.Steps = map[string]graphv1alpha1.EDAGStep{
		step1.Stepname: edag.Spec.Steps[step1.Stepname],
		step2.Stepname: edag.Spec.Steps[step2.Stepname],
	}
	step1Job.Status.Active = 1

	mockedClient.On(
		"FetchResource",
		context.TODO(),
		types.NamespacedName{Name: step1.Name, Namespace: sampleinps.Namespace},
		mock.AnythingOfType("*v1.Job"),
	).Run(func(args mock.Arguments) {
		jobOut := args.Get(2).(*batchv1.Job)
		*jobOut = *step1Job
	}).Return(true, nil).Times(1)

	isfailed, err := mockedService.StartNewJobs(
		context.TODO(), &run, &edag, sampleinps.Namespace, sampleinps.Port, sampleinps.DefaultLabels,
	)

	assert.False(t, isfailed)
	assert.NoError(t, err)
}

func TestStartNewJobsShouldStartNewJobs(t *testing.T) {
	// Steps 1 & 3 complete
	// Should start jobs 2 & 4
	// Should not start job 5

	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient,
		Log:    &newLog,
	}
	sampleinps, edag, run := SampleDataFactory()

	// Jobs 1 & 3 are existent
	run.Status.Jobs = map[string]string{
		sampleinps.Jobs[0].Stepname: sampleinps.Jobs[0].Stepname,
		sampleinps.Jobs[2].Stepname: sampleinps.Jobs[0].Stepname,
	}

	jobMap := map[string]*batchv1.Job{
		sampleinps.Jobs[0].Stepname: SampleJobFactory(sampleinps.Jobs[0], sampleinps),
		sampleinps.Jobs[1].Stepname: SampleJobFactory(sampleinps.Jobs[1], sampleinps),
		sampleinps.Jobs[2].Stepname: SampleJobFactory(sampleinps.Jobs[2], sampleinps),
		sampleinps.Jobs[3].Stepname: SampleJobFactory(sampleinps.Jobs[3], sampleinps),
	}

	jobMap[sampleinps.Jobs[0].Stepname].Status.Active = 0
	jobMap[sampleinps.Jobs[2].Stepname].Status.Active = 0

	getJobDetail := func(args mock.Arguments) {
		jobInp := args.Get(2).(*batchv1.Job)
		name := args.Get(1).(types.NamespacedName)
		fetchedJob := jobMap[name.Name]
		*jobInp = *fetchedJob
	}

	acceptedJobs := []string{
		jobMap[sampleinps.Jobs[1].Stepname].ObjectMeta.Name,
		jobMap[sampleinps.Jobs[3].Stepname].ObjectMeta.Name,
	}
	verifyJobRequest := func(args mock.Arguments) {
		job := args.Get(1).(*batchv1.Job)
		assert.True(t,
			job.Name == acceptedJobs[0] || job.Name == acceptedJobs[1],
		)
	}

	mockedClient.On(
		"FetchResource",
		context.TODO(),
		mock.Anything,
		mock.AnythingOfType("*v1.Job"),
	).Run(getJobDetail).Return(true, nil).Times(4)

	mockedClient.On(
		"CreateJob", context.TODO(), mock.AnythingOfType("*v1.Job"),
	).Run(verifyJobRequest).Return(nil).Times(2)
	mockedClient.On(
		"UpdateStatus", context.TODO(), mock.Anything, mock.Anything,
	).Return(nil).Times(2)
	mockedClient.On(
		"SetControllerReference", mock.Anything, mock.Anything,
	).Return(nil).Times(2)

	isfailed, err := mockedService.StartNewJobs(
		context.TODO(), &run, &edag, sampleinps.Namespace, sampleinps.Port, sampleinps.DefaultLabels,
	)

	assert.False(t, isfailed)
	assert.NoError(t, err)
}

func TestStartNewJobsShouldFailIfJobCreationFails(t *testing.T) {
	// Steps 1 & 3 complete
	// Should start jobs 2 & 4
	// Should not start job 5

	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient,
		Log:    &newLog,
	}
	sampleinps, edag, run := SampleDataFactory()

	// Jobs 1 & 3 are existent
	run.Status.Jobs = map[string]string{
		sampleinps.Jobs[0].Stepname: sampleinps.Jobs[0].Stepname,
		sampleinps.Jobs[2].Stepname: sampleinps.Jobs[0].Stepname,
	}

	jobMap := map[string]*batchv1.Job{
		sampleinps.Jobs[0].Stepname: SampleJobFactory(sampleinps.Jobs[0], sampleinps),
		sampleinps.Jobs[1].Stepname: SampleJobFactory(sampleinps.Jobs[1], sampleinps),
		sampleinps.Jobs[2].Stepname: SampleJobFactory(sampleinps.Jobs[2], sampleinps),
		sampleinps.Jobs[3].Stepname: SampleJobFactory(sampleinps.Jobs[3], sampleinps),
	}

	jobMap[sampleinps.Jobs[0].Stepname].Status.Active = 0
	jobMap[sampleinps.Jobs[2].Stepname].Status.Active = 0

	getJobDetail := func(args mock.Arguments) {
		jobInp := args.Get(2).(*batchv1.Job)
		name := args.Get(1).(types.NamespacedName)
		fetchedJob := jobMap[name.Name]
		*jobInp = *fetchedJob
	}

	acceptedJobs := []string{
		jobMap[sampleinps.Jobs[1].Stepname].ObjectMeta.Name,
		jobMap[sampleinps.Jobs[3].Stepname].ObjectMeta.Name,
	}
	verifyJobRequest := func(args mock.Arguments) {
		job := args.Get(1).(*batchv1.Job)
		assert.True(t,
			job.Name == acceptedJobs[0] || job.Name == acceptedJobs[1],
		)
	}

	mockedClient.On(
		"FetchResource",
		context.TODO(),
		mock.Anything,
		mock.AnythingOfType("*v1.Job"),
	).Run(getJobDetail).Return(true, nil).Times(4)

	createErr := errors.New("Failed to create job")

	mockedClient.On(
		"CreateJob", context.TODO(), mock.AnythingOfType("*v1.Job"),
	).Run(verifyJobRequest).Return(createErr).Times(1)

	_, err := mockedService.StartNewJobs(
		context.TODO(), &run, &edag, sampleinps.Namespace, sampleinps.Port, sampleinps.DefaultLabels,
	)

	assert.Error(t, err)
}

func TestStartNewJobsShouldFailOnFailedJob(t *testing.T) {
	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient,
		Log:    &newLog,
	}
	sampleinps, edag, run := SampleDataFactory()

	run.Status.Jobs = map[string]string{
		sampleinps.Jobs[0].Stepname: sampleinps.Jobs[0].Stepname,
	}

	job1 := SampleJobFactory(sampleinps.Jobs[0], sampleinps)
	job1.Status.Conditions = []batchv1.JobCondition{
		{Type: batchv1.JobSuspended},
		{Type: batchv1.JobFailed},
	}

	getJobDetail := func(args mock.Arguments) {
		jobInp := args.Get(2).(*batchv1.Job)
		*jobInp = *job1
	}

	mockedClient.On(
		"FetchResource",
		context.TODO(),
		mock.Anything,
		mock.AnythingOfType("*v1.Job"),
	).Run(getJobDetail).Return(true, nil).Times(1)

	isfailed, err := mockedService.StartNewJobs(
		context.TODO(), &run, &edag, sampleinps.Namespace, sampleinps.Port, sampleinps.DefaultLabels,
	)

	assert.True(t, isfailed)
	assert.NoError(t, err)
}

func TestStartNewJobsAllJobsFinished(t *testing.T) {
	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient,
		Log:    &newLog,
	}
	sampleinps, edag, run := SampleDataFactory()

	// Jobs 1 & 3 are existent
	run.Status.Jobs = map[string]string{
		sampleinps.Jobs[0].Stepname: sampleinps.Jobs[0].Stepname,
		sampleinps.Jobs[1].Stepname: sampleinps.Jobs[1].Stepname,
		sampleinps.Jobs[2].Stepname: sampleinps.Jobs[2].Stepname,
		sampleinps.Jobs[3].Stepname: sampleinps.Jobs[3].Stepname,
		sampleinps.Jobs[4].Stepname: sampleinps.Jobs[4].Stepname,
	}

	jobMap := map[string]*batchv1.Job{
		sampleinps.Jobs[0].Stepname: SampleJobFactory(sampleinps.Jobs[0], sampleinps),
		sampleinps.Jobs[1].Stepname: SampleJobFactory(sampleinps.Jobs[1], sampleinps),
		sampleinps.Jobs[2].Stepname: SampleJobFactory(sampleinps.Jobs[2], sampleinps),
		sampleinps.Jobs[3].Stepname: SampleJobFactory(sampleinps.Jobs[3], sampleinps),
		sampleinps.Jobs[4].Stepname: SampleJobFactory(sampleinps.Jobs[4], sampleinps),
	}

	for _, job := range jobMap {
		job.Status.Active = 0
	}

	getJobDetail := func(args mock.Arguments) {
		jobInp := args.Get(2).(*batchv1.Job)
		name := args.Get(1).(types.NamespacedName)
		fetchedJob := jobMap[name.Name]
		*jobInp = *fetchedJob
	}

	mockedClient.On(
		"FetchResource",
		context.TODO(),
		mock.Anything,
		mock.AnythingOfType("*v1.Job"),
	).Run(getJobDetail).Return(true, nil).Times(5)

	isfailed, err := mockedService.StartNewJobs(
		context.TODO(), &run, &edag, sampleinps.Namespace, sampleinps.Port, sampleinps.DefaultLabels,
	)

	assert.False(t, isfailed)
	assert.NoError(t, err)
}

func TestStartNewJobsFailedToFetchJobs(t *testing.T) {
	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient,
		Log:    &newLog,
	}
	sampleinps, edag, run := SampleDataFactory()

	// Jobs 1 & 3 are existent
	run.Status.Jobs = map[string]string{
		sampleinps.Jobs[0].Stepname: sampleinps.Jobs[0].Stepname,
	}

	err := errors.New("Failed to get resource")
	mockedClient.On(
		"FetchResource",
		context.TODO(),
		mock.Anything,
		mock.AnythingOfType("*v1.Job"),
	).Return(false, err).Times(1)

	_, returnErr := mockedService.StartNewJobs(
		context.TODO(), &run, &edag, sampleinps.Namespace, sampleinps.Port, sampleinps.DefaultLabels,
	)

	assert.Error(t, returnErr)
}

func TestCheckRunOwnerReferenceShouldCreateOwnersNil(t *testing.T) {
	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient,
		Log:    &newLog,
	}
	sampleinps := SampleInputsFactory()
	run := SampleEDAGRunFactory(sampleinps)
	edag := SampleEDAGFactory(sampleinps)

	mockedClient.On("SetControllerReference", context.TODO(), &edag, &run).Return(nil).Times(1)

	err := mockedService.CheckRunOwnerReference(context.TODO(), &edag, &run)
	assert.NoError(t, err)
}

func TestCheckRunOwnerReferenceShouldReturnErrIfFailed(t *testing.T) {
	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient,
		Log:    &newLog,
	}
	sampleinps := SampleInputsFactory()
	run := SampleEDAGRunFactory(sampleinps)
	edag := SampleEDAGFactory(sampleinps)

	raisederror := errors.New("Failed to set reference")

	mockedClient.On("SetControllerReference", context.TODO(), &edag, &run).Return(raisederror).Times(1)

	err := mockedService.CheckRunOwnerReference(context.TODO(), &edag, &run)
	assert.Equal(t, err, raisederror)
}

func TestCheckRunOwnerReferenceShouldFindExisting(t *testing.T) {
	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient,
		Log:    &newLog,
	}
	sampleinps := SampleInputsFactory()
	run := SampleEDAGRunFactory(sampleinps)
	edag := SampleEDAGFactory(sampleinps)

	newRef := metav1.OwnerReference{
		Kind: "EDAGRun", Name: run.Name,
	}
	edag.OwnerReferences = []metav1.OwnerReference{newRef}

	mockedClient.On("SetControllerReference", context.TODO(), &edag, &run).Return(nil).Times(1)

	err := mockedService.CheckRunOwnerReference(context.TODO(), &edag, &run)
	assert.NoError(t, err)
}

func TestIsRunNotComplete(t *testing.T) {
	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient,
		Log:    &newLog,
	}
	sampleinps := SampleInputsFactory()
	run := SampleEDAGRunFactory(sampleinps)

	assert.False(t, mockedService.IsRunComplete(&run))
}
func TestIsRunCompleteSuccess(t *testing.T) {
	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient,
		Log:    &newLog,
	}
	sampleinps := SampleInputsFactory()
	run := SampleEDAGRunFactory(sampleinps)

	conditions := []metav1.Condition{
		{
			Type:   string(service.RunInProgress),
			Status: metav1.ConditionTrue,
		},
		{
			Type:   string(service.RunSucceeded),
			Status: metav1.ConditionTrue,
		},
	}
	run.Status.Conditions = conditions

	assert.True(t, mockedService.IsRunComplete(&run))
}

func TestIsRunCompleteFailed(t *testing.T) {
	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient,
		Log:    &newLog,
	}
	sampleinps := SampleInputsFactory()
	run := SampleEDAGRunFactory(sampleinps)

	conditions := []metav1.Condition{
		{
			Type:   string(service.RunInProgress),
			Status: metav1.ConditionTrue,
		},
		{
			Type:   string(service.RunFailed),
			Status: metav1.ConditionTrue,
		},
	}
	run.Status.Conditions = conditions

	assert.True(t, mockedService.IsRunComplete(&run))
}

func TestFetchEDAG(t *testing.T) {
	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient,
		Log:    &newLog,
	}
	edagname := types.NamespacedName{
		Name: "someedagname", Namespace: "fakenamespace",
	}
	mockedClient.On(
		"FetchResource", context.TODO(), edagname, mock.AnythingOfType("*v1alpha1.EDAG"),
	).Return(true, nil).Times(1)

	fetchedEdag, err := mockedService.FetchEDAG(
		context.TODO(), edagname,
	)
	assert.NotNil(t, fetchedEdag)
	assert.NoError(t, err)
}

func TestFetchEDAGRun(t *testing.T) {
	newLog := logr.Discard()
	mockedClient := new(MockEDAGRunClient)
	mockedService := service.EDAGRunService{
		Client: mockedClient,
		Log:    &newLog,
	}
	edagrunname := types.NamespacedName{
		Name: "someedagrunname", Namespace: "fakenamespace",
	}
	mockedClient.On(
		"FetchResource", context.TODO(), edagrunname, mock.AnythingOfType("*v1alpha1.EDAGRun"),
	).Return(true, nil).Times(1)

	fetchedEdagrun, err := mockedService.FetchEDAGRun(
		context.TODO(), edagrunname,
	)
	assert.NotNil(t, fetchedEdagrun)
	assert.NoError(t, err)
}

func TestIsJobNotComplete(t *testing.T) {
	sampleinps := SampleInputsFactory()
	job := sampleinps.Jobs[0]
	actualJob := SampleJobFactory(job, sampleinps)
	actualJob.Status.Active = 1

	assert.False(t, service.IsJobComplete(actualJob))
}

func TestIsJobComplete(t *testing.T) {
	sampleinps := SampleInputsFactory()
	job := sampleinps.Jobs[0]
	actualJob := SampleJobFactory(job, sampleinps)
	actualJob.Status.Active = 0

	assert.True(t, service.IsJobComplete(actualJob))
}
