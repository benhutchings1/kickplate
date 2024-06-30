import json
import re
from typing import Union

from kubernetes.client.exceptions import ApiException
from pydantic import BaseModel, ValidationError

from com_utils.error_handling import CustomError
from com_utils.http import HttpCodes
from com_utils.logger import Loggers, LoggingLevel
from config import ApiSettings
from external.kubenetes import KubernetesConn
from routes.create_graph.exec_graph_model import ExecGraph, ExecGraphStep

GRAPH_TYPING = dict[str, Union[str, dict[str, Union[str, dict]]]]


class CreateExecGraph:
    def __init__(self, k8s_client: KubernetesConn) -> None:
        self.__k8s_client = k8s_client

    def submit_graph(self, json_def: GRAPH_TYPING) -> str:
        exec_graph = self.__load_into_model(json_def=json_def)
        return self.__submit_execgraph(
            exec_graph=self.__format_request(graph_model=exec_graph)
        )

    def __load_into_model(self, json_def: GRAPH_TYPING) -> ExecGraph:
        """Load json definition of graph into Pydantic model"""
        try:
            self.__validate_name(json_def["graphname"])

            # load steps
            steps = []
            for step in json_def["steps"]:
                steps.append(ExecGraphStep(**step))

            return ExecGraph(graphname=json_def["graphname"], steps=steps)
        except (ValidationError, TypeError):
            raise CustomError(
                message="Invalid graph definition",
                error_code=HttpCodes.USER_ERROR,
                logging_level=LoggingLevel.INFO,
                logging_message=Loggers.USER_ERROR,
            )
        except KeyError as e:
            raise CustomError(
                message=f"Data {e} missing from graph definition",
                error_code=HttpCodes.USER_ERROR,
                logging_level=LoggingLevel.INFO,
                logger=Loggers.USER_ERROR,
            )

    def __format_request(self, graph_model: ExecGraph) -> dict:
        """Add metadata to make valid resource request"""
        return {
            "apiVersion": ApiSettings.kube_graph_api_version,
            "kind": ApiSettings.kube_graph_kind,
            "metadata": {"name": graph_model.graphname},
            "spec": {"steps": [step.model_dump_json() for step in graph_model.steps]},
        }

    def __validate_name(self, execgraph_name: str) -> None:
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

    def __submit_execgraph(self, exec_graph: GRAPH_TYPING) -> str:
        """Submit graph as custom resource"""
        try:
            # Attempt to create graph resource
            self.__k8s_client.create_resource(
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
