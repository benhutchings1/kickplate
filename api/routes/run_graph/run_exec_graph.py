import json
from random import choices
from string import ascii_lowercase
from kubernetes.dynamic.exceptions import ApiException
from com_utils.error_handling import CustomError
from com_utils.http import HttpCodes
from com_utils.logger import LoggingLevel, Loggers
from external.kubenetes import KubernetesConn
from pydantic import BaseModel
from config import ApiSettings


class ResponseModel(BaseModel):
    execution_id: str


class RunGraph:
    def __init__(
        self,
        graph_name: str,
    ) -> ResponseModel:
        graph_def = self.get_graph_definition(graph_name)

        # generate workflow
        workflow = self.generate_workflow(graph_name, graph_def)

        # submit workflow and return workflow name
        return self.submit_workflow(workflow)

    def get_graph_definition(self, graph_name) -> dict:
        """Gets graph definition as custom resource under given name"""
        try:
            print()
            return KubernetesConn().get_resource(
                name=graph_name,
                group=ApiSettings.kube_graph_group,
                version=ApiSettings.kube_graph_api_version,
                plural=ApiSettings.kube_graph_plural,
                namespace=ApiSettings.kube_namespace,
            )

        except ApiException as e:
            # Check for specific known errors
            if json.loads(e.body)["code"] == 404:
                raise CustomError(
                    message="execution graph '{graph_name}' not found",
                    error_code=HttpCodes.USER_ERROR,
                    logger=Loggers.USER_ERROR,
                    logging_level=LoggingLevel.INFO,
                )
            else:
                # Unknown error, let top level error handler capture it
                raise e

    def generate_workflow(self, graph_name: str, step_definitions: list[dict]) -> dict:
        # Format steps and DAG for execution
        templates = []
        for step_def in step_definitions["spec"]["steps"]:
            templates.append(self.create_template(step_def))
        templates.append(self.create_dag(step_definitions))

        return {
            "apiVersion": ApiSettings.kube_workflow_api_version,
            "kind": ApiSettings.kube_workflow_kind,
            "metadata": {"name": self.generate_name_suffix(graph_name, length=5)},
            "spec": {"entrypoint": "dag-workflow", "templates": templates},
        }

    def generate_name_suffix(graph_name: str, length: int) -> str:
        """Adds *length* lowercase ascii characters to end of graph_name"""
        return graph_name + "-" + "".join(choices(ascii_lowercase, k=length))

    def create_template(sd) -> dict:
        return {
            "name": sd["stepname"] + "-template",
            "container": {
                "image": sd["image"],
                "command": sd["command"],
                "args": sd["args"],
            },
        }

    def create_dag(sd) -> dict:
        tasks = []
        for step in sd["spec"]["steps"]:
            tasks.append(
                {
                    "name": step["stepname"],
                    "template": step["stepname"] + "-template",
                    "dependencies": step["dependencies"],
                }
            )
        return {"name": "dag-workflow", "dag": {"tasks": tasks}}

    def submit_workflow(self, workflow: dict[str]) -> str:
        try:
            KubernetesConn().create_resource(
                group=ApiSettings.kube_workflow_group,
                version=ApiSettings.kube_workflow_api_version,
                plural=ApiSettings.kube_workflow_plural,
                namespace=ApiSettings.kube_namespace,
                body=workflow,
            )
            return workflow["metadata"]["name"]
        except ApiException as e:
            # Check for specific known errors
            if json.loads(e.body)["code"] == 409:
                raise CustomError(
                    error_code=HttpCodes.INTERNAL_SERVER_ERROR,
                    logging_message=f"'{workflow['metadata']['name']}'\
                        already exists",
                    logger=Loggers.USER_ERROR,
                    logging_level=LoggingLevel.INFO,
                )
            else:
                # Unknown error, let top level error handler capture it
                raise e
