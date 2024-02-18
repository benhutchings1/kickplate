resource "azurerm_container_registry" "acr" {
  name = "${var.resource_prefix}acr"
  location = var.location
  resource_group_name = var.resource_prefix
  sku = "Standard"
}