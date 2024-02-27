param(
    [int]$RecordsNumber,
    [string]$CosmosAccountName,
    [string]$DatabaseName,
    [string]$CollectionID
)
$global:ErrorActionPreference = "Stop"
$global:VerbosePreference = "Continue"

Write-Verbose "Executing initialization_script"

# COSMOS
Write-Host "##vso[task.setvariable variable=COSMOS_ACCOUNT_NAME;]$CosmosAccountName"
Write-Host "##vso[task.setvariable variable=DATABASE_NAME;]$DatabaseName"
Write-Host "##vso[task.setvariable variable=COLLECTION_ID;]$CollectionID"
Write-Host "##vso[task.setvariable variable=RECORDS_NUMBER;]$RecordsNumber"

# Entra ID
Write-Host "##vso[task.setvariable variable=AZURE_CLIENT_ID;]$env:servicePrincipalId"
Write-Host "##vso[task.setvariable variable=AZURE_CLIENT_SECRET;]$env:servicePrincipalKey"
Write-Host "##vso[task.setvariable variable=AZURE_TENANT_ID;]$env:tenantId"