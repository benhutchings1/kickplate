from config import ApiSettings
from com_utils.error_handling import CustomError
from com_utils.http import HttpCodes
from com_utils.logger import LoggingLevel
from kubernetes import client
from urllib3.exceptions import MaxRetryError
from kubernetes.client.rest import ApiException
import json


class KubernetesConn:
    def __init__(self) -> None:
        self.kube_client_config = client.Configuration()
        self.kube_client_config.host = ApiSettings.kube_host
        self.kube_client_config.ssl_ca_cert = ApiSettings.kube_client_cert_path
        self.kube_client_config.api_key = {
            "authorization": "Bearer " + ApiSettings.kube_service_account_key
        }
        self.kube_client = client.ApiClient(self.kube_client_config)

    @staticmethod
    def __exception_catcher(func):
        def exception_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except MaxRetryError as e:
                raise CustomError(
                    error_code=HttpCodes.INTERNAL_SERVER_ERROR,
                    logging_message=f"Error connecting to k8,\
                        error message {e.reason}",
                    # Critical as core functionality
                    logging_level=LoggingLevel.CRITICAL,
                )

        return exception_wrapper

    @__exception_catcher
    def create_resource(
        self,
        group,
        version,
        namespace,
        plural,
        body,
    ):
        try:
            client.CustomObjectsApi(self.kube_client).create_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                body=body,
            )
        except ApiException as e:
            # Check for specific known errors
            if json.loads(e.body)["code"] == 404:
                # Let missing resource get handled by user
                raise e
            else:
                # Unknown error, let top level error handler capture it
                raise CustomError(
                    error_code=HttpCodes.INTERNAL_SERVER_ERROR,
                    logging_message=f"Error creating custom object \
                        group={group} \
                        version={version} \
                        namespace={namespace} \
                        plural={plural} \
                        body={body} \
                        Error: {str(e)}",
                    # Critical as core functionality
                    logging_level=LoggingLevel.CRITICAL,
                )

    @__exception_catcher
    def get_resource(self, name, group, version, namespace, plural):
        try:
            client.CustomObjectsApi(self.kube_client).get_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                name=name,
            )
        except ApiException as e:
            raise CustomError(
                error_code=HttpCodes.INTERNAL_SERVER_ERROR,
                logging_message=f"Error getting custom object \
                    name={name} \
                    group={group} \
                    version={version} \
                    namespace={namespace} \
                    plural={plural} \
                    Error: {str(e)}",
                # Critical as core functionality
                logging_level=LoggingLevel.CRITICAL,
            )
