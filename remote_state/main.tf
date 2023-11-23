terraform {
   backend "azurerm" {
        storage_account_name = "${var.resource_prefix}-storage"
        container_name = "${var.resource_prefix}-file"
        use_azuread_auth = true
        
        subscription_id = "${var.sub_id}"
        tenant_id = "${var.ten_id}"
    }
}

# Resource group to hold storage
resource "azurerm_resource_group" "tfstate" {
  name = "${var.resource_prefix}-rg"
  location = var.location
}
# Setup files storage
resource "azurerm_storage_account" "tfstate-storage" {
  name = "${var.resource_prefix}-storage"
  location = var.location
  resource_group_name = azurerm_resource_group.tfstate.name
  account_replication_type = "LRS"
  account_tier = "Cold"
}

resource "azurerm_storage_share_file" "name" {
  name = "${var.resource_prefix}-file"
  storage_share_id = azurerm_storage_account.tfstate-storage.id
}