# Hashicorp Vault

## Introduction

This module will deploy hashicorp vault into a pre-existing AKS cluster
<br />

<!--- BEGIN_TF_DOCS --->

<!--- END_TF_DOCS --->

<br />

## Example

~~~~
provider "azurerm" {
  version = ">=2.0.0"
  features {}
  subscription_id = "00000-0000-0000-0000-0000000"
}

# Subscription
module "subscription" {
  source = "git@github.com:LexisNexis-TFE/module-subscription-data.git?ref=v1.0.0"
}

# Metadata
module "metadata" {
  source = "git@github.com:LexisNexis-TFE/module-metadata.git?ref=v1.0.0"

  subscription_id     = module.subscription.output.subscription_id
  # These values should be taken from https://github.com/openrba/python-azure-naming
  business_unit       = "rba.businessUnit"
  cost_center         = "rba.costCenter"
  environment         = "rba.environment"
  location            = "rba.azureRegion"
  market              = "rba.market"
  product_name        = "rba.productName"
  product_group       = "rba.productGroup"
  project             = "project-url"
  sre_team            = "team-name"
  subscription_type   = "rba.subscriptionType"
  resource_group_type = "rba.resourceGroupType"

  additional_tags = {
    "example" = "an additional tag"
  }
}

# Resource group
module "resource_group" {
  source = "git@github.com:LexisNexis-TFE/module-resource-group.git?ref=v1.0.0"

  location = module.metadata.location
  tags     = module.metadata.tags
  name     = module.metadata.names
}

# AKS
## This will create a managed kubernetes cluster
module "aks" {
  source = "git@gitlab.ins.risk.regn.net:azure/kubernetes.git"

  service_principal_id     = var.service_principal_id
  service_principal_secret = var.service_principal_secret
  service_principal_name   = "ris-azr-app-infrastructure-aks-test"

  resource_group_name = module.resource_group.name
  location            = module.resource_group.location

  names = module.metadata.names
  tags  = module.metadata.tags

  kubernetes_version = "1.16.7"

  default_node_pool_name                = "default"
  default_node_pool_vm_size             = "Standard_D2s_v3"
  default_node_pool_enable_auto_scaling = true
  default_node_pool_node_min_count      = 1
  default_node_pool_node_max_count      = 5
  default_node_pool_availability_zones  = [1,2,3]

  enable_kube_dashboard = true
  
}

# Kubernetes
## (Optional) add new storage class for geo-redundant storage
provider "kubernetes" {
  load_config_file       = "false"
  host                   = module.aks.host
  client_certificate     = base64decode(module.aks.client_certificate)
  client_key             = base64decode(module.aks.client_key)
  cluster_ca_certificate = base64decode(module.aks.cluster_ca_certificate)
}

resource "kubernetes_storage_class" "azurefile_grs" {
   metadata {
     name = "azurefile-grs"
   }
   storage_provisioner = "kubernetes.io/azure-file"
   reclaim_policy      = "Retain"
   parameters = {
     skuName = "Standard_GRS"
   }
   mount_options = ["dir_mode=0777", "file_mode=0777", "uid=0", "gid=0", "mfsymlinks", "cache=strict"]
}

# Vault
## This will setup a vault cluster with a raft storage backend using azurefile GRS
module "vault" {
  source = "git@gitlab.ins.risk.regn.net:azure/hashicorp-vault.git"

  kubectl_host                   = module.aks.host
  kubectl_username               = module.aks.username
  kubectl_password               = module.aks.password
  kubectl_client_certificate     = module.aks.client_certificate
  kubectl_client_key             = module.aks.client_key
  kubectl_cluster_ca_certificate = module.aks.cluster_ca_certificate

  subscription_id                 = module.subscription.output.subscription_id
  aks_service_principal_client_id = module.aks.service_principal_client_id

  resource_group_name = module.resource_group.name
  location            = module.resource_group.location

  names = module.metadata.names
  tags  = module.metadata.tags

  azure_key_vault_id                  = module.key_vault.id
  azure_key_vault_name                = module.key_vault.name
  azure_key_vault_resource_group_name = module.key_vault.resource_group_name

  vault_enable_ha              = true
  vault_enable_raft_backend    = true
  vault_version                = "1.4.0"
  vault_agent_injector_version = "0.3.0"
  vault_data_storage_class     = "azurefile-grs"

}
~~~~
