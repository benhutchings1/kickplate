terraform {
  required_version = "=1.6.1"
  required_providers {
    azurerm = {
        source = "hashicorp/azurerm"
        version = "3.81.0"
    }
  }
  backend "local" {}
}

provider "azurerm" {
  tenant_id = var.tenant_id
  subscription_id = var.subscription_id
  
  features { }
}