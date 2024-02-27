# List and create documents in CosmosDB

## 1.0 Introduction

This repository has the code to be able to connect to an Azure Cosmos DB database by performing role-based access control (RBAC) and get a list of documents in a specific collection and create documents.

## 2.0 File Structure

- **create-document.yaml**: Azure Pipeline to execute the creation of a document in a collection.
- **list-documents.yaml**: Azure Pipeline to get the list of a documents in a collection.
- **cosmos_db_create_document**: Folder with the scripts, execution and inizializer.
  - initialization_script.ps1: It collects the data it receives from the pipeline and transforms it to send it as environment variables to be used in the create_cosmos_document.py script.
  - create_cosmos_document.py: Script to authenticate against the database and create a document in the collection.
- **cosmos_db_list_documents**: Folder with the scripts, execution and inizializer.
  - initialization_script.ps1: It collects the data it receives from the pipeline and transforms it to send it as environment variables to be used in the list_cosmos_documents.py script.
  - list_cosmos_documents.py: Script to authenticate against the database and get a list of all documents in a collection.

## 3.0 RBAC

In order to make these calls, the identity (in this case a service principal) has the role of Cosmos DB Built-in Data Contributor.
[CosmosDB RBAC Documentation](https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-setup-rbac#built-in-role-definitions)

Example of terraform code for this purpose:

```hcl
data "azurerm_cosmosdb_sql_role_definition" "builtin_data_contributor" {
  resource_group_name = data.azurerm_resource_group.rg_01.name
  account_name        = azurerm_cosmosdb_account.account.name
  role_definition_id  = "00000000-0000-0000-0000-000000000002"
}

resource "azurerm_cosmosdb_sql_role_assignment" "spn_db_contributor" {
  name                = "00000000-0000-0000-0000-000000000002"
  resource_group_name = data.azurerm_resource_group.rg_01.name
  account_name        = azurerm_cosmosdb_account.account.name
  role_definition_id  = data.azurerm_cosmosdb_sql_role_definition.builtin_data_contributor.id
  principal_id        = data.azurerm_client_config.current.object_id
  scope               = azurerm_cosmosdb_account.account.id
}

```

## 4.0 Requirements

### 4.1 Azure Credentials

In order to get a valid token for Entra ID you need to pass the values for the identity in the following environment variables:

- AZURE_CLIENT_ID
- AZURE_CLIENT_SECRET
- AZURE_TENANT_ID

If you are using a user managed identity you may only need to give a value for AZURE_CLIENT_ID on the other hand if you are using a service principal you will need to fill in all three values.

This is one of the tasks performed by the inicialization_script.ps1 by the way.

```powershell
# Entra ID
Write-Host "##vso[task.setvariable variable=AZURE_CLIENT_ID;]$env:servicePrincipalId"
Write-Host "##vso[task.setvariable variable=AZURE_CLIENT_SECRET;]$env:servicePrincipalKey"
Write-Host "##vso[task.setvariable variable=AZURE_TENANT_ID;]$env:tenantId"
```

### 4.2 Mandatory parameters for the Python scripts

#### 4.2.1 create_cosmos_document.py

This script get the following parameters from environment variables for create a document with this data:

- **COSMOS_ACCOUNT_NAME**: string for the cosmos account.
- **DATABASE_NAME**: string with the name of the database.
- **COLLECTION_ID**: string with the name of the collection id.
- **CREATE_BODY**: A JSON file in base64 encoded with a valid body used in the cosmos [Create a document REST API](https://learn.microsoft.com/en-us/rest/api/cosmos-db/create-a-document#body).
- The previous parameters explained in [4.1](#azure_client)

#### 4.2.2 list_cosmos_documents.py

This script get the following parameters from environment variables for get a list with all documents with this data:
    - **COSMOS_ACCOUNT_NAME**: string for the cosmos account.
    - **DATABASE_NAME**: string with the name of the database.
    - **COLLECTION_ID**: string with the name of the collection id
    - **RECORDS_NUMBER**: Number of documents to be logged in the log sorted by the newest ones.

## 5.0 Initialization_script scripts

A PowerShell (Core) script that receives the necessary parameters and converts them and creates environment variables to be used in python scripts.

## 6.0 Pipelines

### 6.1 Create CosmosDB Document

#### 6.1.1 Input Parameters

The pipeline has the following input parameters:
| Name | Mandatory | Type | Description | Example |
|--|--|--|--|--|
| CreateBody | Yes | String | The body to create a new document. | { 'param1' : 'param1value', 'param2' : 'param2value', 'param3' : []} |
| CosmosAccountName | Yes | String | Cosmos Account Name to create a new document. | mycosmosdb01 |
| DatabaseName | Yes | String | Cosmos Database to create a new document. | db01 |
| CollectionID | Yes | String | CollectionID where the document will be created. | coll01 |

#### 6.1.2 Tasks

The pipeline has three tasks:

- **AzureCLI@2 Inicialize Context**:  Receives the pipeline parameters, transforms them and generates environment variables to be used as input parameters in the python script execution task.
- **Script**:  install the libraries needed by the Python Script with pip.
- **PythonScript@0 Create CosmosDB Document**: Python script that creates a document using the environment variables created in the first task.

### 6.1 Get a list of CosmosDB Documents

The pipeline has the following input parameters:
| Name | Mandatory | Type | Description | Example |
|--|--|--|--|--|
| NumberOfDocuments | No | Number | Number of documents to be logged in the log sorted by the newest ones. Default value is 10 | 20 |
| CosmosAccountName | Yes | String | Cosmos Account Name to create a new document. | mycosmosdb01 |
| DatabaseName | Yes | String | Cosmos Database to create a new document. | db01 |
| CollectionID | Yes | String | CollectionID where the document will be created. | coll01 |

#### 6.2.2 Tasks

The pipeline has three tasks:

- **AzureCLI@2 Inicialize Context**:  Receives the pipeline parameters, transforms them and generates environment variables to be used as input parameters in the python script execution task.
- **Script**:  install the libraries needed by the Python Script with pip.
- **PythonScript@0 Create CosmosDB Document**: Python script that get a list of documents using the environment variables created in the first task.
