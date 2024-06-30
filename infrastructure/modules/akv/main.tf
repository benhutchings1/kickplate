resource "azurerm_key_vault" "akv" {
    name                = "${var.env}-de-kv"
    tenant_id           = var.tenant_id
    location            = var.location
    resource_group_name = azurerm_resource_group.parent_rg.name
    sku_name            = "standard"
    tags                = local.tags
}