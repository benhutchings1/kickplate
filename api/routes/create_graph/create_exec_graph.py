import json
import re
from pydantic import BaseModel
from kubernetes.client.exceptions import ApiException
from routes.create_graph.exec_graph_model import ExecGraph, ExecGraphStep
from com_utils.logger import LoggingLevel, Loggers
from com_utils.error_handling import CustomError
from com_utils.http import HttpCodes
from external.kubenetes import KubernetesConn
from config import ApiSettings


class CreateExecGraph:
    def __init__(self, json_def: dict) -> None:
        exec_graph = self.load_into_model(json_def=json_def)

        return self.submit_execgraph(
            exec_graph=self.format_request(graph_model=exec_graph)
        )

    def load_into_model(self, json_def: dict) -> ExecGraph:
        """Load json definition of graph into Pydantic model"""
        self.validate_name(json_def["graphname"])

        try:
            # load steps
            steps = []
            for step in json_def["steps"]:
                steps.append(ExecGraphStep(**step))

            return ExecGraph(graphname=json_def["graphname"], steps=steps)
        except KeyError as e:
            raise CustomError(
                message=f"Data {e} missing from graph definition",
                error_code=HttpCodes.USER_ERROR,
                logging_level=LoggingLevel.INFO,
                logger=Loggers.USER_ERROR,
            )

    def format_request(self, graph_model: ExecGraph) -> dict:
        """Add metadata to make valid resource request"""
        return {
            "apiVersion": ApiSettings.kube_graph_api_version,
            "kind": ApiSettings.kube_graph_kind,
            "metadata": {"name": graph_model.graphname},
            "spec": {"steps": [step.model_dump_json() for step in graph_model.steps]},
        }

    def validate_name(self, execgraph_name: str) -> None:
        # Check graph name against regex
        regex_engine = re.compile(
            "[a-z0-9]([-a-z0-9]*[a-z0-9])?(\\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*"
        )
        if not bool(regex_engine.match(execgraph_name)):
            raise CustomError(
                message=f"graph name [{execgraph_name}] must consist\
                    of lower case alphanumeric characters, '-', or '.', \
                        and must start/end with an alphanumeric character",
                error_code=HttpCodes.USER_ERROR,
                logging_level=LoggingLevel.INFO,
                logger=Loggers.USER_ERROR,
            )

    def submit_execgraph(self, exec_graph: dict) -> str:
        """Submit graph as custom resource"""
        try:
            # Attempt to create graph resource
            KubernetesConn().create_resource(
                group=ApiSettings.kube_graph_group,
                version=ApiSettings.kube_graph_api_version,
                plural=ApiSettings.kube_graph_plural,
                namespace=ApiSettings.kube_namespace,
                body=exec_graph,
            )
            return exec_graph["metadata"]["name"]
        except ApiException as e:
            # Check for specific known errors
            if str(json.loads(e.body)["code"]) == str(409):
                raise CustomError(
                    message=f"{exec_graph['metadata']['name']} already exists",
                    error_code=HttpCodes.CONFLICT,
                    logger=Loggers.USER_ERROR,
                    logging_level=LoggingLevel.INFO,
                )
            else:
                # Unknown error, let top level error handler capture it
                raise e


class ResponseModel(BaseModel):
    graph_name: str
