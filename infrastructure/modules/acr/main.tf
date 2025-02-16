locals {
  acr_name = "kickplate${var.env}"
}

resource "azurerm_container_registry" "acr" {
  name                = local.acr_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.sku
  tags                = var.tags
}
