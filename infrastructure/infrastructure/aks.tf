module "de_aks" {
  source = "../modules/aks"

  resource_group_name = azurerm_resource_group.parent_rg.name
  env = var.env
  location = var.location
  dns_prefix = "de-${var.env}-"
  tags = local.tags

  engine_node_pools = [{
        name = "model_node_pool_1"
        vm_size = "Standard_D2_v2"
        node_count = 2
    }]
}