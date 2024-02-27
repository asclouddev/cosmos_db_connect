param(
    [string]$CreateBody,
    [string]$CosmosAccountName,
    [string]$DatabaseName,
    [string]$CollectionID
)

$global:ErrorActionPreference = "Stop"
$global:VerbosePreference = "Continue"

Write-Verbose "Executing initialization_script"
Write-Verbose "json: $CreateBody"
$base64String = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($CreateBody))

# COSMOS
Write-Host "##vso[task.setvariable variable=CREATE_BODY;]$base64String"
Write-Host "##vso[task.setvariable variable=COSMOS_ACCOUNT_NAME;]$CosmosAccountName"
Write-Host "##vso[task.setvariable variable=DATABASE_NAME;]$DatabaseName"
Write-Host "##vso[task.setvariable variable=COLLECTION_ID;]$CollectionID"

# Entra ID
Write-Host "##vso[task.setvariable variable=AZURE_CLIENT_ID;]$env:servicePrincipalId"
Write-Host "##vso[task.setvariable variable=AZURE_CLIENT_SECRET;]$env:servicePrincipalKey"
Write-Host "##vso[task.setvariable variable=AZURE_TENANT_ID;]$env:tenantId"