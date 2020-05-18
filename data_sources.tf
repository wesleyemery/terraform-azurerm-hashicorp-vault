data "azurerm_client_config" "current" {}

data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

#data "azurerm_key_vault" "kv" {
#  name                = var.azure_key_vault_name
#  resource_group_name = var.azure_key_vault_resource_group_name
#}