resource "azurerm_kubernetes_cluster" "aks" {
  location            = var.location
  name                = "kickplate-${var.env}-aks"
  resource_group_name = var.resource_group_name
  dns_prefix          = var.dns_prefix

  tags = var.tags

  identity {
    type = "SystemAssigned"
  }


  default_node_pool {
    name       = "systemnodes"
    vm_size    = var.system_node_pool.vm_size
    node_count = 1
  }

  network_profile {
    network_plugin    = "kubenet"
    load_balancer_sku = "standard"
  }
}


resource "azurerm_kubernetes_cluster_node_pool" "worker-node-pools" {
  for_each              = { for pool in var.worker_node_pools : pool.name => pool }
  name                  = each.value.name
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks.id
  vm_size               = each.value.vm_size
  node_count            = each.value.node_count
}


resource "azurerm_role_assignment" "aks_to_acr" {
  scope                = var.acr_id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
}
