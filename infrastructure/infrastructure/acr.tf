module "kickplate-container-registry" {
  source = "../modules/acr"

  resource_group_name = azurerm_resource_group.parent_rg.name
  location            = var.location
  env                 = var.env
  sku                 = "Standard"
  tags                = local.tags
}
