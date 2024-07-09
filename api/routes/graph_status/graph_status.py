from typing import Union

from kubernetes.client.exceptions import ApiException
import json

from com_utils.error_handling import CustomError
from com_utils.http import HttpCodes
from com_utils.logger import Loggers, LoggingLevel
from config import ApiSettings
from external.kubenetes import K8_Client

from .graph_status_model import GraphStatusModel, StepStatus


class GraphStatus:
    def __init__(self, k8s_client: K8_Client):
        """
        Top level API function for getting status of an execution graph\n
        Inputs\n
            - execution_id (str): execution identifier\n
            - token (str): Bearer token provided by Azure Entra ID\n
        Output\n
            - execution_description (json): description of execution\n
        """
        self.k8s_client = k8s_client

    def get_graph_status(self, execution_id: str) -> dict:
        return self.__extract_information(
            self.__get_execution_description(execution_id=execution_id)
        ).model_dump()

    def __get_execution_description(self, execution_id: str) -> dict:
        try:
            return self.k8s_client.get_resource(
                name=execution_id,
                group=ApiSettings.kube_workflow_group,
                version=ApiSettings.kube_workflow_api_version,
                plural=ApiSettings.kube_workflow_plural,
                namespace=ApiSettings.kube_namespace,
            )
        except ApiException as e:
            if json.loads(e.body)["code"] == "404":
                raise CustomError(
                    message=f"Graph: {execution_id} not found",
                    error_code=HttpCodes.NOT_FOUND,
                    logger=Loggers.USER_ERROR,
                    logging_level=LoggingLevel.INFO,
                )
            else:
                raise e

    def __extract_information(
        self, exec_desc: dict[str, Union[str, dict]]
    ) -> GraphStatusModel:
        overall_labels = exec_desc["metadata"]["labels"]
        steps_desc = exec_desc["status"]["nodes"]

        # Pop DAG graph definition
        graphname = exec_desc["metadata"]["name"]
        steps_desc.pop(graphname, None)

        # Get overall information
        return GraphStatusModel(
            graphname=graphname,
            completed_time=overall_labels.get("workflows.argoproj.io/completed", None),
            phase=overall_labels.get("workflows.argoproj.io/phase", None),
            creation_time=exec_desc["metadata"].get("creationTimestamp", None),
            steps_status=[
                StepStatus(
                    name=step["displayName"],
                    state=step["phase"],
                    start_time=step["startedAt"],
                    finish_time=step.get("finishedAt", None),
                    error_message=step.get("message", None),
                )
                for step in steps_desc.values()
            ],
        )
