from com_utils.http import HttpCodes
from kubernetes.client.exceptions import ApiException
from external.kubenetes import KubernetesConn
from com_utils.error_handling import CustomError
from com_utils.logger import LoggingLevel, Loggers
from .graph_status_model import GraphStatusModel, StepStatus
from config import ApiSettings


class GraphStatus:
    def __init__(self, execution_id: str):
        """
        Top level API function for getting status of an execution graph\n
        Inputs\n
            - execution_id (str): execution identifier\n
            - token (str): Bearer token provided by Azure Entra ID\n
        Output\n
            - execution_description (json): description of execution\n
        """
        return self.extract_information(
            self.get_execution_description(execution_id=execution_id)
        ).model_dump_json()

    def get_execution_description(self, execution_id: str) -> dict:
        try:
            return KubernetesConn().get_resource(
                name=execution_id,
                group=ApiSettings.kube_workflow_group,
                version=ApiSettings.kube_workflow_api_version,
                plural=ApiSettings.kube_workflow_plural,
                namespace=ApiSettings.kube_namespace,
            )
        except ApiException:
            # Get 404 raised error
            raise CustomError(
                message=f"Graph: {execution_id} not found",
                error_code=HttpCodes.NOT_FOUND,
                logger=Loggers.USER_ERROR,
                logging_level=LoggingLevel.INFO,
            )

    def extract_information(self, exec_desc: dict[str, str]) -> GraphStatusModel:
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
                    finish_time=step["finishedAt"],
                    error_message=step["message"],
                )
                for step in steps_desc.values()
            ],
        )
