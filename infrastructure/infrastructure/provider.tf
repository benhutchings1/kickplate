terraform {
  required_version = "=1.9.7"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.81.0"
    }
  }
  backend "azurerm" {}
}

provider "azurerm" {
  skip_provider_registration = true
  subscription_id            = var.subscription_id
  tenant_id                  = var.tenant_id

  features {}
}
