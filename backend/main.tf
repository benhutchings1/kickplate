locals {
  tags = {
    "Terraform": true,
    "Repo": "https://github.com/benhutchings1/deployment-engine",
  }
}

resource "azurerm_resource_group" "tfstate_rg" {
    name = "ben-${var.env}-rg"
    location = var.location

    tags = local.tags
}

resource "azurerm_storage_account" "tfstate_store" {
    name = "bentfstatestore"
    resource_group_name = azurerm_resource_group.tfstate_rg.name
    location = var.location
    account_tier = "Standard"
    account_replication_type = "LRS"

    tags = local.tags
}

resource "azurerm_storage_container" "tfstate_store_container" {
    name = "tfstate"
    storage_account_name = azurerm_storage_account.tfstate_store.name
}