from external.kubenetes import KubernetesConn
from config import ApiSettings

KubernetesConn().get_resource(
    name="busbox",
    group=ApiSettings.kube_workflow_group,
    version=ApiSettings.kube_graph_api_version,
    namespace=ApiSettings.kube_namespace,
    plural=ApiSettings.kube_workflow_plural,
)
