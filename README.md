# Hashicorp Vault

## Introduction

This module will deploy hashicorp vault into a pre-existing AKS cluster
<br />

<!--- BEGIN_TF_DOCS --->
## Providers

| Name | Version |
|------|---------|
| azurerm | >= 2.0.0 |
| helm | >= 1.2.1 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:-----:|
| identity\_name | name for Azure identity to be used by AAD | `string` | `"aks-aad"` | no |
| kubectl\_client\_certificate | kubernetes client certificate | `string` | n/a | yes |
| kubectl\_client\_key | kubernetes certificate key | `string` | n/a | yes |
| kubectl\_cluster\_ca\_certificate | kubernetes certificate bundle | `string` | n/a | yes |
| kubectl\_host | kubernetes hostname | `string` | n/a | yes |
| kubernetes\_namespace | kubernetes namespace where vault will be installed | `string` | `"default"` | no |
| location | Azure Region | `string` | n/a | yes |
| names | names to be applied to resources | `map(string)` | n/a | yes |
| resource\_group\_name | Resource group name | `string` | n/a | yes |
| subscription\_id | Azure Subscription ID | `string` | n/a | yes |
| tags | tags to be applied to resources | `map(string)` | n/a | yes |
| vault\_agent\_injector\_sidecar\_version | version of Vault Agent Injectort sidecar to install (defaults to <vault\_version>) | `string` | `""` | no |
| vault\_agent\_injector\_version | version of Vault Agent Injector to install | `string` | `"0.3.0"` | no |
| vault\_audit\_data\_storage\_size | vault audit logs storage size | `string` | `"10Gi"` | no |
| vault\_audit\_storage\_class | kubernetes storage class to use for vault audit logs | `string` | `"null"` | no |
| vault\_audit\_storage\_size | vault audit storage size | `string` | `"10Gi"` | no |
| vault\_data\_storage\_class | kubernetes storage class to use for vault data | `string` | `"null"` | no |
| vault\_data\_storage\_size | vault data storage size | `string` | `"10Gi"` | no |
| vault\_enable\_audit\_storage | kubernetes storage class to use for vault audit logs | `string` | `false` | no |
| vault\_enable\_data\_storage | enable data storage for raft/file storage backend | `bool` | `true` | no |
| vault\_enable\_ha | enable ha (clustering) | `bool` | `true` | no |
| vault\_enable\_raft\_backend | enable raft storage backend | `bool` | `true` | no |
| vault\_helm\_chart\_version | version of vault helm chart to use | `string` | `"0.5.0"` | no |
| vault\_version | version of Vault to install | `string` | `"1.4.0"` | no |

## Outputs

No output.
<!--- END_TF_DOCS --->