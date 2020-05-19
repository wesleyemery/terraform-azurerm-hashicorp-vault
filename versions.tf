terraform {
  required_version = ">= 0.12.10"
  
  required_providers {
    helm = ">= 1.2.1"
  }
}

provider "azurerm" {
  version = ">= 2.0.0"
  features {}
  subscription_id = var.subscription_id
}