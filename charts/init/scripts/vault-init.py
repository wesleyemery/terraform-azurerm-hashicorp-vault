try:
  import requests
except ImportError:
  print('Installing required module: requests')
  import subprocess
  subprocess.check_output('/usr/local/bin/pip install requests', shell=True) 
import requests

try:
  import base64
except ImportError:
  print('Installing required module: base64')
  import subprocess
  subprocess.check_output('/usr/local/bin/pip install base64', shell=True) 
import base64

# Setup retry strategy
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

vault_api_retry_strategy = Retry(
    total=10,
    status_forcelist=[404, 429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "PUT"],
    backoff_factor=2
)
vault_api_adapter = HTTPAdapter(max_retries=vault_api_retry_strategy)
vault_api = requests.Session()
vault_api.mount("https://", vault_api_adapter)
vault_api.mount("http://", vault_api_adapter)

azure_api_retry_strategy = Retry(
    total=5,
    status_forcelist=[404, 429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "PUT"],
    backoff_factor=2
)
azure_api_adapter = HTTPAdapter(max_retries=azure_api_retry_strategy)
az_api = requests.Session()
az_api.mount("https://", azure_api_adapter)
az_api.mount("http://", azure_api_adapter)

### Get API token to use with Azure Key Vault
TOKEN_URL='http://169.254.169.254/metadata/identity/oauth2/token'
TOKEN_PARAMS={'api-version': '2018-02-01','resource': 'https://vault.azure.net'}
TOKEN_URL_HEADERS={'Metadata': 'true'}

print('Getting Azure API Token.....')
try:
  token_request = az_api.get(url=TOKEN_URL, params=TOKEN_PARAMS, headers=TOKEN_URL_HEADERS) 
except:
  raise Exception('There was an problem connecting to the Azure metadata API from the vault-init pod')

if token_request.status_code == requests.codes.ok:
  try:
    access_token = token_request.json()['access_token']
  except:
    raise Exception('There was a problem setting the access_token')
  print('Azure API token successfully retrieved')
else:
  raise Exception('Unable to retrieve Azure API token')

### Test connectivity to Azure Key Vault
AZURE_KEY_VAULT_SECRET_URL='{{ .Values.azureKeyVaultSecretUrl }}'
AZURE_KEY_VAULT_PARAMS={'api-version': '7.0'}
AZURE_KEY_VAULT_HEADERS={'Authorization': "Bearer %s" % (access_token)}

print('Testing connectivity to Azure Key Vault secret.....')
try:
  azure_key_vault_request = az_api.get(url=AZURE_KEY_VAULT_SECRET_URL, params=AZURE_KEY_VAULT_PARAMS, headers=AZURE_KEY_VAULT_HEADERS)
except:
  raise Exception('There was an problem connecting to the Azure Key Vault API from the vault-init pod')

if azure_key_vault_request.status_code == requests.codes.ok:
  print("Successfully connected to Azure Key Vault")
else:
  raise Exception('Unable to write to Azure Key Vault Secret')

### Test connectivity to Hashicorp Vault
VAULT_HEALTH_URL='http://vault-0.vault-internal:8200/v1/sys/health'
VAULT_HEALTH_PARAMS={'uninitcode': '999'}

print('Testing Hashicorp Vault health.....')
try:
  vault_health_request = vault_api.get(url=VAULT_HEALTH_URL, params=VAULT_HEALTH_PARAMS)
except:
  raise Exception('There was an problem getting the Hashicorp Vault health status')

if vault_health_request.status_code == 999:
  print("Successfully connected to uninitialized Hashicorp Vault")
elif vault_health_request.status_code == requests.codes.ok:
  print("Hashicorp Vault is already initialized, exiting")
  exit(0) 
else:
  print(vault_health_request.status_code)
  raise Exception('Unable to get Hashicorp Vault health status')

### Initialize Hashicorp Vault
VAULT_INIT_URL='http://vault-0.vault-internal:8200/v1/sys/init'
VAULT_INIT_JSON={'recovery_shares': 5, 'recovery_threshold': 3}

print('Initializing Hashicorp Vault.....')
try:
  init_request = vault_api.post(url=VAULT_INIT_URL, json=VAULT_INIT_JSON)
except:
  raise Exception('There was an problem connecting to the Hashicorp Vault API on pod vault-0')

if init_request.status_code == requests.codes.ok:
  print("Hashicorp Vault initialized successfully")
else:
  raise Exception('Hashicorp Vault initialization failed')

## Write Hashicorp Vault initialization information to Azure Key Vault
AZURE_KEY_VAULT_JSON={'value': "%s" % (init_request.json())}
AZURE_KEY_VAULT_JSON["tags"]=eval(base64.b64decode('{{ .Values.azureKeyVaultSecretTags }}').decode("utf-8"))

print('Writing Hashicorp Vault initialization information to Azure Key Vault secret.....')
try:
  azure_key_vault_request = az_api.put(url=AZURE_KEY_VAULT_SECRET_URL, params=AZURE_KEY_VAULT_PARAMS, headers=AZURE_KEY_VAULT_HEADERS, json=AZURE_KEY_VAULT_JSON)
except:
  raise Exception('There was an problem connecting to the Azure Key Vault API from the vault-init pod')

if azure_key_vault_request.status_code == requests.codes.ok:
  print("Vault Initialization information successfully written to %s" % (AZURE_KEY_VAULT_SECRET_URL))
else:
  raise Exception('Unable to write to Azure Key Vault Secret')