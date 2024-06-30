resource "azurerm_container_registry" "de_acr" {
    name                = "deployment_engine_${var.env}_acr"
    resource_group_name = var.resource_group_name
    location            = var.location
    sku                 = var.sku
    tags                = var.tags
}