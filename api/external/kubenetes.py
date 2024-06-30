from kubernetes import client
from urllib3.exceptions import MaxRetryError

from com_utils.error_handling import CustomError
from com_utils.http import HttpCodes
from com_utils.logger import LoggingLevel
from config import ApiSettings


class KubernetesConn:
    def __init__(self) -> None:
        self.k8_client_cfg = client.Configuration()
        self.k8_client_cfg.host = ApiSettings.kube_host
        self.k8_client_cfg.ssl_ca_cert = ApiSettings.kube_client_cert_path
        self.k8_client_cfg.api_key = {
            "authorization": "Bearer " + ApiSettings.kube_service_account_key
        }
        self.k8_client = client.ApiClient(self.k8_client_cfg)

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
        group: str,
        version: str,
        namespace: str,
        plural: str,
        body: str,
    ):
        client.CustomObjectsApi(self.k8_client).create_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            body=body,
        )

    @__exception_catcher
    def get_resource(
        self, name: str, group: str, version: str, namespace: str, plural: str
    ):
        client.CustomObjectsApi(self.k8_client).get_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            name=name,
        )
