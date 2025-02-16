resource "azurerm_user_assigned_identity" "aksid" {
  location            = var.location
  name                = "id-aks-${var.env}"
  resource_group_name = azurerm_resource_group.parent_rg.name
}
