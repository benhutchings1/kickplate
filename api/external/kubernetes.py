from kubernetes_asyncio import client
from settings import settings


class KubernetesClient:
    async def __init__(self) -> None:
        self.cluster_config = client.Configuration()
        self.cluster_config.host = settings.CLUSTER_HOST
        self.cluster_config.ssl_ca_cert = settings.CLUSTER_CERTIFICATE_PATH
        self.cluster_config.api_key = {
            "authorization": "Bearer " + settings.CLUSTER_SERVICE_ACCOUNT_SECRET
        }
        self.cluster_client = client.ApiClient(self.cluster_config)

    async def create_resource(
        self,
        group: str,
        version: str,
        namespace: str,
        plural: str,
        body: str,
    ):
        await client.CustomObjectsApi(self.cluster_client).create_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            body=body,
        )

    async def get_resource(
        self, name: str, group: str, version: str, namespace: str, plural: str
    ):
        return await client.CustomObjectsApi(self.cluster_client).get_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            name=name,
        )
