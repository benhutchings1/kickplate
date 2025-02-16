module "aks" {
  source = "../modules/aks"

  resource_group_name = azurerm_resource_group.parent_rg.name
  env                 = var.env
  location            = var.location
  dns_prefix          = "kickplate-${var.env}"
  tags                = local.tags
  system_node_pool = {
    node_count = 1
    vm_size    = "Standard_D2_v2"
  }


  worker_node_pools = [{
    name       = "modelpool"
    vm_size    = "Standard_D2_v2"
    node_count = 2
  }]

  acr_id = module.kickplate-container-registry.id
}

