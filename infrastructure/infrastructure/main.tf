resource "azurerm_resource_group" "parent_rg" {
    name = "de-${var.env}-rg"
    location = "${var.location}"
    tags = local.tags
}