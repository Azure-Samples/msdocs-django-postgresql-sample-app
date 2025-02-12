@description('The location used for all deployed resources')
param location string = resourceGroup().location

@description('Tags that will be applied to all resources')
param tags object = {}


@secure()
param databasePassword string
param msdocsDjangoPostgresqlSampleAppExists bool
@secure()
param msdocsDjangoPostgresqlSampleAppDefinition object

@description('Id of the user or app to assign application roles')
param principalId string

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = uniqueString(subscription().id, resourceGroup().id, location)

// Monitor application with Azure Monitor
module monitoring 'br/public:avm/ptn/azd/monitoring:0.1.0' = {
  name: 'monitoring'
  params: {
    logAnalyticsName: '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    applicationInsightsName: '${abbrs.insightsComponents}${resourceToken}'
    applicationInsightsDashboardName: '${abbrs.portalDashboards}${resourceToken}'
    location: location
    tags: tags
  }
}

// Container registry
module containerRegistry 'br/public:avm/res/container-registry/registry:0.1.1' = {
  name: 'registry'
  params: {
    name: '${abbrs.containerRegistryRegistries}${resourceToken}'
    location: location
    acrAdminUserEnabled: true
    tags: tags
    publicNetworkAccess: 'Enabled'
    roleAssignments:[
      {
        principalId: msdocsDjangoPostgresqlSampleAppIdentity.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
      }
    ]
  }
}

// Container apps environment
module containerAppsEnvironment 'br/public:avm/res/app/managed-environment:0.4.5' = {
  name: 'container-apps-environment'
  params: {
    logAnalyticsWorkspaceResourceId: monitoring.outputs.logAnalyticsWorkspaceResourceId
    name: '${abbrs.appManagedEnvironments}${resourceToken}'
    location: location
    zoneRedundant: false
  }
}
var databaseName = 'DATA-TEST'
var databaseUser = 'psqladmin'
module postgreServer 'br/public:avm/res/db-for-postgre-sql/flexible-server:0.1.4' = {
  name: 'postgreServer'
  params: {
    // Required parameters
    name: '${abbrs.dBforPostgreSQLServers}${resourceToken}'
    skuName: 'Standard_B1ms'
    tier: 'Burstable'
    // Non-required parameters
    administratorLogin: databaseUser
    administratorLoginPassword: databasePassword
    geoRedundantBackup: 'Disabled'
    passwordAuth:'Enabled'
    firewallRules: [
      {
        name: 'AllowAllIps'
        startIpAddress: '0.0.0.0'
        endIpAddress: '255.255.255.255'
      }
    ]
    databases: [
      {
        name: databaseName
      }
    ]
    location: location
  }
}

module msdocsDjangoPostgresqlSampleAppIdentity 'br/public:avm/res/managed-identity/user-assigned-identity:0.2.1' = {
  name: 'msdocsDjangoPostgresqlSampleAppidentity'
  params: {
    name: '${abbrs.managedIdentityUserAssignedIdentities}msdocsDjangoPostgresqlSampleApp-${resourceToken}'
    location: location
  }
}

module msdocsDjangoPostgresqlSampleAppFetchLatestImage './modules/fetch-container-image.bicep' = {
  name: 'msdocsDjangoPostgresqlSampleApp-fetch-image'
  params: {
    exists: msdocsDjangoPostgresqlSampleAppExists
    name: 'msdocs-django-postgresql-sample-app'
  }
}

var msdocsDjangoPostgresqlSampleAppAppSettingsArray = filter(array(msdocsDjangoPostgresqlSampleAppDefinition.settings), i => i.name != '')
var msdocsDjangoPostgresqlSampleAppSecrets = map(filter(msdocsDjangoPostgresqlSampleAppAppSettingsArray, i => i.?secret != null), i => {
  name: i.name
  value: i.value
  secretRef: i.?secretRef ?? take(replace(replace(toLower(i.name), '_', '-'), '.', '-'), 32)
})
var msdocsDjangoPostgresqlSampleAppEnv = map(filter(msdocsDjangoPostgresqlSampleAppAppSettingsArray, i => i.?secret == null), i => {
  name: i.name
  value: i.value
})

module msdocsDjangoPostgresqlSampleApp 'br/public:avm/res/app/container-app:0.8.0' = {
  name: 'msdocsDjangoPostgresqlSampleApp'
  params: {
    name: 'msdocs-django-postgresql-sample-app'
    ingressTargetPort: 80
    scaleMinReplicas: 1
    scaleMaxReplicas: 10
    secrets: {
      secureList:  union([
        {
          name: 'db-pass'
          value: databasePassword
        }
        {
          name: 'db-url'
          value: 'postgresql://${databaseUser}:${databasePassword}@${postgreServer.outputs.fqdn}:5432/${databaseName}'
        }
      ],
      map(msdocsDjangoPostgresqlSampleAppSecrets, secret => {
        name: secret.secretRef
        value: secret.value
      }))
    }
    containers: [
      {
        image: msdocsDjangoPostgresqlSampleAppFetchLatestImage.outputs.?containers[?0].?image ?? 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
        name: 'main'
        resources: {
          cpu: json('0.5')
          memory: '1.0Gi'
        }
        env: union([
          {
            name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
            value: monitoring.outputs.applicationInsightsConnectionString
          }
          {
            name: 'AZURE_CLIENT_ID'
            value: msdocsDjangoPostgresqlSampleAppIdentity.outputs.clientId
          }
          {
            name: 'POSTGRES_HOST'
            value: postgreServer.outputs.fqdn
          }
          {
            name: 'POSTGRES_USERNAME'
            value: databaseUser
          }
          {
            name: 'POSTGRES_DATABASE'
            value: databaseName
          }
          {
            name: 'POSTGRES_PASSWORD'
            secretRef: 'db-pass'
          }
          {
            name: 'POSTGRES_URL'
            secretRef: 'db-url'
          }
          {
            name: 'POSTGRES_PORT'
            value: '5432'
          }
          {
            name: 'PORT'
            value: '80'
          }
        ],
        msdocsDjangoPostgresqlSampleAppEnv,
        map(msdocsDjangoPostgresqlSampleAppSecrets, secret => {
            name: secret.name
            secretRef: secret.secretRef
        }))
      }
    ]
    managedIdentities:{
      systemAssigned: false
      userAssignedResourceIds: [msdocsDjangoPostgresqlSampleAppIdentity.outputs.resourceId]
    }
    registries:[
      {
        server: containerRegistry.outputs.loginServer
        identity: msdocsDjangoPostgresqlSampleAppIdentity.outputs.resourceId
      }
    ]
    environmentResourceId: containerAppsEnvironment.outputs.resourceId
    location: location
    tags: union(tags, { 'azd-service-name': 'msdocs-django-postgresql-sample-app' })
  }
}
// Create a keyvault to store secrets
module keyVault 'br/public:avm/res/key-vault/vault:0.6.1' = {
  name: 'keyvault'
  params: {
    name: '${abbrs.keyVaultVaults}${resourceToken}'
    location: location
    tags: tags
    enableRbacAuthorization: false
    accessPolicies: [
      {
        objectId: principalId
        permissions: {
          secrets: [ 'get', 'list' ]
        }
      }
      {
        objectId: msdocsDjangoPostgresqlSampleAppIdentity.outputs.principalId
        permissions: {
          secrets: [ 'get', 'list' ]
        }
      }
    ]
    secrets: [
      {
        name: 'db-pass'
        value: databasePassword
      }
    ]
  }
}
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.uri
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
output AZURE_RESOURCE_MSDOCS_DJANGO_POSTGRESQL_SAMPLE_APP_ID string = msdocsDjangoPostgresqlSampleApp.outputs.resourceId
output AZURE_RESOURCE_DATA_TEST_ID string = '${postgreServer.outputs.resourceId}/databases/DATA-TEST'
