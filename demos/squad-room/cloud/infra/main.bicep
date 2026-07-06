// Squad Room — hero-tools MCP server on Azure Container Apps.
// Provisions Log Analytics + a Container Apps environment + the MCP server app.
// The image is built in ACR (az acr build) BEFORE this deploys — see deploy.ps1.
@description('Location for all resources.')
param location string = resourceGroup().location

@description('Short name used to derive resource names.')
param appName string = 'squadroom-mcp'

@description('Existing Azure Container Registry name that holds the built image.')
param acrName string

@description('Fully-qualified container image, e.g. myacr.azurecr.io/squadroom-mcp:latest')
param containerImage string

@description('Container listen port.')
param targetPort int = 8000

var resourceToken = uniqueString(subscription().id, resourceGroup().id, appName)

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-${resourceToken}'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: acrName
}

// User-assigned identity created FIRST so AcrPull is granted before the app pulls the image.
// (A system-assigned identity causes a chicken-and-egg: the app must pull the image at creation
// time, but its principalId — and therefore the AcrPull role — only exists after creation.)
resource uami 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-${resourceToken}'
  location: location
}

// Grant the identity AcrPull on the registry BEFORE the app is created.
resource acrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, uami.id, 'AcrPull')
  scope: acr
  properties: {
    principalId: uami.properties.principalId
    principalType: 'ServicePrincipal'
    // AcrPull role definition id.
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  }
}

resource env 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-${resourceToken}'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${uami.id}': {} }
  }
  // Ensure AcrPull is in place before the app attempts its first image pull.
  dependsOn: [ acrPull ]
  properties: {
    managedEnvironmentId: env.id
    configuration: {
      ingress: {
        external: true
        targetPort: targetPort
        transport: 'auto'
        // MCP streamable-HTTP is long-lived; disable session affinity but allow generous timeouts.
        allowInsecure: false
      }
      registries: [
        {
          server: acr.properties.loginServer
          identity: uami.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: appName
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
          env: [
            { name: 'PORT', value: string(targetPort) }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

@description('The public MCP endpoint. Append to the toolbox mcp entry server_url.')
output mcpServerUrl string = 'https://${app.properties.configuration.ingress.fqdn}/mcp'
output containerAppFqdn string = app.properties.configuration.ingress.fqdn
