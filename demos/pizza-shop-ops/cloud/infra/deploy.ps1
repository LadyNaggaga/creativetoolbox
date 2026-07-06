<#
.SYNOPSIS
  Deploy the Pizza Shop Ops hero-tools MCP server to Azure Container Apps — no local Docker needed
  (the image is built server-side with `az acr build`).

.DESCRIPTION
  1. Creates the resource group and an Azure Container Registry.
  2. Builds the MCP server image in ACR from cloud/mcp-server/Dockerfile (context = demo root).
  3. Deploys the Container Apps environment + app via cloud/infra/main.bicep.
  4. Prints the public MCP endpoint to paste into cloud/toolbox.yaml.

.EXAMPLE
  ./deploy.ps1 -ResourceGroup rg-pizza-cloud -Location eastus
#>
param(
  [Parameter(Mandatory = $true)] [string]$ResourceGroup,
  [string]$Location = 'eastus',
  [string]$AcrName = "pizzaacr$(([System.BitConverter]::ToString((New-Object Security.Cryptography.SHA256Managed).ComputeHash([Text.Encoding]::UTF8.GetBytes($ResourceGroup))).Replace('-','').ToLower().Substring(0,10)))",
  [string]$ImageTag = 'pizzashop-mcp:latest'
)

$ErrorActionPreference = 'Stop'
# This script lives in cloud/infra/. The Docker build context is the demo root (two levels up),
# so the image can bundle ../../mock-backends.
$demoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path   # demos/pizza-shop-ops
$dockerfile = Join-Path $PSScriptRoot '..\mcp-server\Dockerfile'   # cloud/mcp-server/Dockerfile
$bicep = Join-Path $PSScriptRoot 'main.bicep'                       # cloud/infra/main.bicep
Write-Host "Demo root (build context): $demoRoot"

az group create --name $ResourceGroup --location $Location --output none
Write-Host "Resource group '$ResourceGroup' ready."

az acr create --resource-group $ResourceGroup --name $AcrName --sku Basic --output none
$loginServer = az acr show --name $AcrName --query loginServer -o tsv
Write-Host "ACR '$AcrName' ready ($loginServer)."

Write-Host "Building image in ACR (server-side, no local Docker)..."
az acr build `
  --registry $AcrName `
  --file $dockerfile `
  --image $ImageTag `
  $demoRoot | Out-Host

$image = "$loginServer/$ImageTag"
Write-Host "Deploying Container App with image $image ..."
$deployment = az deployment group create `
  --resource-group $ResourceGroup `
  --template-file $bicep `
  --parameters acrName=$AcrName containerImage=$image `
  --query 'properties.outputs' -o json | ConvertFrom-Json

$mcpUrl = $deployment.mcpServerUrl.value
Write-Host ""
Write-Host "===================================================================="
Write-Host " MCP server deployed."
Write-Host "   MCP endpoint: $mcpUrl"
Write-Host ""
Write-Host " Next: put this URL in cloud/toolbox.yaml (the pizza mcp entry server_url),"
Write-Host " then run: azd ai toolbox create pizza-shop-ops --from-file ./cloud/toolbox.yaml"
Write-Host "===================================================================="
