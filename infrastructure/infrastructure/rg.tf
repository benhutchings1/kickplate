resource "azurerm_resource_group" "parent_rg" {
    name = "kickplate-${var.env}-rg"
    location = "${var.location}"
    tags = local.tags
}