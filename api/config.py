from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class _ApiSettings(BaseSettings):
    # OAuth Config
    auth_enable: bool = True
    auth_scope: str = "api://268da6d1-91b3-4cf6-88a8-90837d84d94d/groups"
    auth_audience: str = "api://268da6d1-91b3-4cf6-88a8-90837d84d94d"
    auth_issuer: str = "https://sts.windows.net/301dacd7-60f1-42bf-84ce-a38206717103/"
    authorize_endpoint: str = (
        "https://login.microsoftonline.com/301dacd7-60f1-42bf-84ce-a38206717103/oauth2/v2.0/authorize"
    )
    auth_token_endpoint: str = (
        "https://login.microsoftonline.com/301dacd7-60f1-42bf-84ce-a38206717103/oauth2/v2.0/token"
    )
    auth_open_id_config: str = (
        "https://login.microsoftonline.com/301dacd7-60f1-42bf-84ce-a38206717103/v2.0/.well-known/openid-configuration"
    )
    auth_tenant_id: str = "301dacd7-60f1-42bf-84ce-a38206717103"
    auth_group_id: str = "7cf78882-1f33-44b9-9c41-13fc239b64c8"
    auth_client_id: str = "268da6d1-91b3-4cf6-88a8-90837d84d94d"
    auth_redirect_url: str = "https://localhost"
    auth_user_groups: List[str] = [""]

    # Kubernetes Config
    kube_host: str = "https://127.0.0.1:32769"
    kube_service_account_key: str
    kube_client_cert_path: str = "cert/"
    kube_namespace: str = "argo"

    # Graph definitions
    kube_graph_api_version: str = "v1"
    kube_graph_kind: str = "ExecutionGraph"
    kube_graph_plural: str = "execgraphs"
    kube_graph_group: str = "test.deploymentengine.com"

    # Workflow definitions
    kube_workflow_api_version: str = "v1alpha1"
    kube_workflow_kind: str = "Workflow"
    kube_workflow_plural: str = "workflows"
    kube_workflow_group: str = "argoproj.io"

    model_config = SettingsConfigDict(env_file=".env")


ApiSettings = _ApiSettings()
