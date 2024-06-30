import json
from random import choices
from string import ascii_lowercase

from kubernetes.client.exceptions import ApiException
from pydantic import BaseModel

from com_utils.error_handling import CustomError
from com_utils.http import HttpCodes
from com_utils.logger import Loggers, LoggingLevel
from config import ApiSettings
from external.kubenetes import KubernetesConn


class ResponseModel(BaseModel):
    execution_id: str


class RunGraph:
    def __init__(self, k8s_client: KubernetesConn):
        self.k8s_client = k8s_client

    def run_graph(self, graph_name: str) -> ResponseModel:
        graph_def = self.__get_graph_definition(graph_name)

        # generate workflow
        workflow = self.__generate_workflow(graph_name, graph_def)

        # submit workflow and return workflow name
        return self.__submit_workflow(workflow)

    def __get_graph_definition(self, graph_name) -> dict:
        """Gets graph definition as custom resource under given name"""
        try:
            return self.k8s_client.get_resource(
                name=graph_name,
                group=ApiSettings.kube_graph_group,
                version=ApiSettings.kube_graph_api_version,
                plural=ApiSettings.kube_graph_plural,
                namespace=ApiSettings.kube_namespace,
            )

        except ApiException as e:
            # Check for specific known errors
            if json.loads(e.body)["code"] == "404":
                raise CustomError(
                    message="execution graph '{graph_name}' not found",
                    error_code=HttpCodes.USER_ERROR,
                    logger=Loggers.USER_ERROR,
                    logging_level=LoggingLevel.INFO,
                )
            else:
                # Unknown error, let top level error handler capture it
                raise e

    def __generate_workflow(
        self, graph_name: str, step_definitions: list[dict]
    ) -> dict:
        # Format steps and DAG for execution
        templates = []
        for step_def in step_definitions["spec"]["steps"]:
            templates.append(self.__create_template(step_def))
        templates.append(self.__create_dag(step_definitions))

        return {
            "apiVersion": ApiSettings.kube_workflow_api_version,
            "kind": ApiSettings.kube_workflow_kind,
            "metadata": {"name": self.__generate_name_suffix(graph_name, length=5)},
            "spec": {"entrypoint": "dag-workflow", "templates": templates},
        }

    @staticmethod
    def __generate_name_suffix(graph_name: str, length: int) -> str:
        """Adds *length* lowercase ascii characters to end of graph_name"""
        return graph_name + "-" + "".join(choices(ascii_lowercase, k=length))

    @staticmethod
    def __create_template(step_def) -> dict:
        return {
            "name": step_def["stepname"] + "-template",
            "container": {
                "image": step_def["image"],
                "command": step_def["command"],
                "args": step_def["args"],
            },
        }

    @staticmethod
    def __create_dag(step_def) -> dict:
        tasks = []
        for step in step_def["spec"]["steps"]:
            tasks.append(
                {
                    "name": step["stepname"],
                    "template": step["stepname"] + "-template",
                    "dependencies": step["dependencies"],
                }
            )
        return {"name": "dag-workflow", "dag": {"tasks": tasks}}

    def __submit_workflow(self, workflow: dict[str]) -> str:
        try:
            self.k8s_client.create_resource(
                group=ApiSettings.kube_workflow_group,
                version=ApiSettings.kube_workflow_api_version,
                plural=ApiSettings.kube_workflow_plural,
                namespace=ApiSettings.kube_namespace,
                body=workflow,
            )
            return workflow["metadata"]["name"]
        except ApiException as e:
            # Check for specific known errors
            if json.loads(e.body)["code"] == "409":
                raise CustomError(
                    error_code=HttpCodes.USER_ERROR,
                    message=f"'{workflow['metadata']['name']}'\
                        already exists",
                    logging_message=f"'{workflow['metadata']['name']}'\
                        already exists",
                    logger=Loggers.USER_ERROR,
                    logging_level=LoggingLevel.INFO,
                )
            else:
                # Unknown error, let top level error handler capture it
                raise e
