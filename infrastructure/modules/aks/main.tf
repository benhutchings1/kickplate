resource "azurerm_kubernetes_cluster" "aks" {
    location                = var.location
    name                    = "deployment-engine-aks-${var.env}"
    resource_group_name     = var.resource_group_name
    dns_prefix              = var.dns_prefix

    identity {
      type                  = "SystemAssigned"
    }
    
    default_node_pool {
      name                  = "deployment-engine-default-node-pool"
      vm_size               = var.system_node_pool.vm_size
      node_count            = var.system_node_pool.node_count
    }   
}