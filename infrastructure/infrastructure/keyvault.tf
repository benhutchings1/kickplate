resource "azurerm_key_vault" "kv" {
  name                = "kv-${var.env}-kickplate"
  location            = var.location
  resource_group_name = azurerm_resource_group.parent_rg.name
  tenant_id           = var.tenant_id
  sku_name            = "standard"
}
