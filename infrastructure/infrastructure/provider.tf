terraform {
  required_version = "=1.6.1"
  required_providers {
    azurerm = {
        source  = "hashicorp/azurerm"
        version = "3.81.0"
    }
  }
  # backend "azurerm" {}
}

provider "azurerm" {
    subscription_id     = var.subscription_id
    tenant_id           = var.tenant_id
    
    features {}
}