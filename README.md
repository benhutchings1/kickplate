# Kickplate
## Introduction
Kickplate is a execution platform, offering simple scalability for all forms of distributed application. Kickplate fully secured with Keycloak SSO identity management, scaled with Kubernetes, managed with a Python FastAPI, and interacted with using a React-based front-end. This is all deployed on Azure, managed by Terraform

<i>Note: Kickplate is a work in progress, running end-to-end graph is unavailable.</i>

## Usage
*Execution Directed Acyclical Graph [EDAG]*

The core building block of the platform is the EDAG. An EDAG describes a collection of steps which execute some code. These steps can be run with many replicas and in parallel.

Example EDAG
```
{
  "name": "myEDAG",
  "steps": [
    {
      "name": "step1",
      "image": "sampleimage/latest",
      "replicas": 3,
      "dependencies": [
        "step0",
        "step2"
      ],
      "envs": {
        "environment": "sbx"
      },
      "arguments": [
        "python",
        "main.py"
      ],
      "commands": [
        "pipenv",
        "shell"
      ]
    },
    ...
  ]
}
```
This EDAG describes a step called `step1` which runs `3 replicas` of the latest `sampleimage` image, each given the environment variable `environment: sbx`. This step is dependent on `step0` and `step2`, which are required to finish before running this step. These images are run with the commands `pipenv shell` and arguments `python main.py`.
### Options Description

| Option | Description | Required |
|----|----| --- |
| Name (overall)| The overall name of the EDAG | True
| Steps | A collection of steps to run, there is no inherent order to the steps, the operator starts with steps without dependents. | True
| Name (step) | The name of the step, used to reference for dependency and results outputs| True
| Replicas | The number of clones of the step to run in parallel | False (default: 1)
| Dependencies | Steps that need to complete (sucessfully) before this is executed | False |
| Envs | key-pair environment variables added to each step replica environment | False |
| Arguments | AKA. Docker CMD. [More Info](https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/) | False |
| Commands | AKA Docker Entrypoint. The initial command run to trigger step execution | False *(but may not trigger execution without)*  |

### Getting started
See API documentation as an entrypoint to the platform.

## Further Documentation
- [Architecture]("./docs/architecture.md)
- [Front End Design]("./docs/web-design.md")