param name string
param location string
param resourceToken string
param principalId string
param tags object
@secure()
param databasePassword string
@secure()
param secretKey string
var appName = '${name}-${resourceToken}'

var pgServerName = '${appName}-server'

resource virtualNetwork 'Microsoft.Network/virtualNetworks@2024-01-01' = {
  name: '${appName}-vnet'
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
    subnets: [
      {
        name: 'database-subnet'
        properties: {
          addressPrefix: '10.0.0.0/24'
          delegations: [
            {
              name: '${appName}-subnet-delegation'
              properties: {
                serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers'
              }
            }
          ]
          privateEndpointNetworkPolicies: 'Enabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
      {
        name: 'webapp-subnet'
        properties: {
          addressPrefix: '10.0.1.0/24'
          delegations: [
            {
              name: 'dlg-appServices'
              properties: {
                serviceName: 'Microsoft.Web/serverFarms'
              }
            }
          ]
        }
      }
      {
        name: 'cache-subnet'
        properties:{
          addressPrefix: '10.0.2.0/24'
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
      {
        name: 'vault-subnet'
        properties: {
          addressPrefix: '10.0.3.0/24'
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
    ]
  }
  resource subnetForDb 'subnets' existing = {
    name: 'database-subnet'
  }
  resource subnetForVault 'subnets' existing = {
    name: 'vault-subnet'
  }
  resource subnetForApp 'subnets' existing = {
    name: 'webapp-subnet'
  }
  resource subnetForCache 'subnets' existing = {
    name: 'cache-subnet'
  }
}

// Resources needed to secure Key Vault behind a private endpoint
resource privateDnsZoneKeyVault 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.vaultcore.azure.net'
  location: 'global'
  resource vnetLink 'virtualNetworkLinks@2020-06-01' = {
    location: 'global'
    name: '${appName}-vaultlink'
    properties: {
      virtualNetwork: {
        id: virtualNetwork.id
      }
      registrationEnabled: false
    }
  }
}
resource vaultPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-04-01' = {
  name: '${appName}-vault-privateEndpoint'
  location: location
  properties: {
    subnet: {
      id: virtualNetwork::subnetForVault.id
    }
    privateLinkServiceConnections: [
      {
        name: '${appName}-vault-privateEndpoint'
        properties: {
          privateLinkServiceId: keyVault.id
          groupIds: ['vault']
        }
      }
    ]
  }
  resource privateDnsZoneGroup 'privateDnsZoneGroups@2024-01-01' = {
    name: 'default'
    properties: {
      privateDnsZoneConfigs: [
        {
          name: 'vault-config'
          properties: {
            privateDnsZoneId: privateDnsZoneKeyVault.id
          }
        }
      ]
    }
  }
}

resource privateDnsZoneDB 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: '${pgServerName}.private.postgres.database.azure.com'
  location: 'global'
  tags: tags
  dependsOn: [
    virtualNetwork
  ]
  resource privateDnsZoneLinkDB 'virtualNetworkLinks@2024-06-01' = {
    name: '${appName}-dblink'
    location: 'global'
    properties: {
      virtualNetwork: {
        id: virtualNetwork.id
      }
      registrationEnabled: false
    }
  }  
}

// Resources needed to secure Redis Cache behind a private endpoint
resource cachePrivateEndpoint 'Microsoft.Network/privateEndpoints@2024-03-01' = {
  name: '${appName}-cache-privateEndpoint'
  location: location
  properties: {
    subnet: {
      id: virtualNetwork::subnetForCache.id
    }
    privateLinkServiceConnections: [
      {
        name: '${appName}-cache-privateEndpoint'
        properties: {
          privateLinkServiceId: redisCache.id
          groupIds: ['redisCache']
        }
      }
    ]
  }
  resource privateDnsZoneGroup 'privateDnsZoneGroups' = {
    name: 'default'
    properties: {
      privateDnsZoneConfigs: [
        {
          name: 'cache-config'
          properties: {
            privateDnsZoneId: privateDnsZoneCache.id
          }
        }
      ]
    }
  }
}
resource privateDnsZoneCache 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.redis.cache.windows.net'
  location: 'global'
  dependsOn: [
    virtualNetwork
  ]
  resource privateDnsZoneLinkCache 'virtualNetworkLinks@2020-06-01' = {
    name: '${appName}-cachelink'
    location: 'global'
    properties: {
      virtualNetwork: {
        id: virtualNetwork.id
      }
      registrationEnabled: false
    }
  }  
}

// The Key Vault is used to manage SQL database and redis secrets.
// Current user has the admin permissions to configure key vault secrets, but by default doesn't have the permissions to read them.
resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: '${take(replace(appName, '-', ''), 17)}-vault'
  location: location
  properties: {
    enableRbacAuthorization: true
    tenantId: subscription().tenantId
    sku: { family: 'A', name: 'standard' }
    // Only allow requests from the private endpoint in the VNET.
    publicNetworkAccess: 'Disabled' // To see the secret in the portal, change to 'Enabled' 
    networkAcls: {
      defaultAction: 'Deny' // To see the secret in the portal, change to 'Allow' 
      bypass: 'None' 
    }
  }
}

// Grant the current user with key vault secret user role permissions over the key vault. This lets you inspect the secrets, such as in the portal
// If you remove this section, you can't read the key vault secrets, but the app still has access with its managed identity.
resource keyVaultSecretUserRoleRoleDefinition 'Microsoft.Authorization/roleDefinitions@2018-01-01-preview' existing = {
  scope: subscription()
  name: '4633458b-17de-408a-b874-0445c86b69e6' // The built-in Key Vault Secret User role
}
resource keyVaultSecretUserRoleAssignment 'Microsoft.Authorization/roleAssignments@2020-08-01-preview' = {
  scope: keyVault
  name: guid(resourceGroup().id, principalId, keyVaultSecretUserRoleRoleDefinition.id)
  properties: {
    roleDefinitionId: keyVaultSecretUserRoleRoleDefinition.id
    principalId: principalId
    principalType: 'User'
  }
}

resource dbserver 'Microsoft.DBforPostgreSQL/flexibleServers@2022-01-20-preview' = {
  location: location
  tags: tags
  name: pgServerName
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    version: '12'
    administratorLogin: 'postgresadmin'
    administratorLoginPassword: databasePassword
    storage: {
      storageSizeGB: 128
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    network: {
      delegatedSubnetResourceId: virtualNetwork::subnetForDb.id
      privateDnsZoneArmResourceId: privateDnsZoneDB.id
    }
    highAvailability: {
      mode: 'Disabled'
    }
    maintenanceWindow: {
      customWindow: 'Disabled'
      dayOfWeek: 0
      startHour: 0
      startMinute: 0
    }
  }

  resource db 'databases@2024-08-01' = {
    name: '${appName}-database'
  }
  dependsOn: [
    privateDnsZoneDB::privateDnsZoneLinkDB
  ]
}

// The Redis cache is configured to the minimum pricing tier
resource redisCache 'Microsoft.Cache/redis@2024-11-01' = {
  name: '${appName}-cache'
  location: location
  properties: {
    sku: {
      name: 'Basic'
      family: 'C'
      capacity: 0
    }
    redisConfiguration: {}
    enableNonSslPort: false
    redisVersion: '6'
    publicNetworkAccess: 'Disabled'
  }
}

// The App Service plan is configured to the B1 pricing tier
resource appServicePlan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: '${appName}-plan'
  location: location
  kind: 'linux'
  properties: {
    reserved: true
  }
  sku: {
    name: 'B1'
  }
}

resource web 'Microsoft.Web/sites@2024-04-01' = {
  name: appName
  location: location
  tags: union(tags, { 'azd-service-name': 'web' }) // Needed by AZD
  properties: {
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12' // Set to Python 3.12
      ftpsState: 'Disabled'
      appCommandLine: 'startup.sh'
      minTlsVersion: '1.2'
    }
    serverFarmId: appServicePlan.id
    httpsOnly: true
  }
  identity: {
    type: 'SystemAssigned'
  }

  // For app setting configuration see the appsettings resource
  
  // Disable basic authentication for FTP and SCM
  resource ftp 'basicPublishingCredentialsPolicies@2023-12-01' = {
    name: 'ftp'
    properties: {
      allow: false
    }
  }
  resource scm 'basicPublishingCredentialsPolicies@2023-12-01' = {
    name: 'scm'
    properties: {
      allow: false
    }
  }

  // Enable App Service native logs
  resource logs 'config' = {
    name: 'logs'
    properties: {
      applicationLogs: {
        fileSystem: {
          level: 'Verbose'
        }
      }
      detailedErrorMessages: {
        enabled: true
      }
      failedRequestsTracing: {
        enabled: true
      }
      httpLogs: {
        fileSystem: {
          enabled: true
          retentionInDays: 1
          retentionInMb: 35
        }
      }
    }
  }

  // Enable VNET integration
  resource webappVnetConfig 'networkConfig' = {
    name: 'virtualNetwork'
    properties: {
      subnetResourceId: virtualNetwork::subnetForApp.id
    }
  }

  dependsOn: [ virtualNetwork ]
}

// Service Connector from the app to the key vault, which generates the connection settings for the App Service app
// The application code doesn't make any direct connections to the key vault, but the setup expedites the managed identity access
// so that the cache connector can be configured with key vault references.
resource vaultConnector 'Microsoft.ServiceLinker/linkers@2024-04-01' = {
  scope: web
  name: 'vaultConnector'
  properties: {
    clientType: 'python'
    targetService: {
      type: 'AzureResource'
      id: keyVault.id
    }
    authInfo: {
      authType: 'systemAssignedIdentity' // Use a system-assigned managed identity. No password is used.
    }
    vNetSolution: {
      type: 'privateLink'
    }
  }
  dependsOn: [
    vaultPrivateEndpoint
  ]
}

// Connector to the PostgreSQL database, which generates the connection string for the App Service app
resource dbConnector 'Microsoft.ServiceLinker/linkers@2024-04-01' = {
  scope: web
  name: 'defaultConnector'
  properties: {
    targetService: {
      type: 'AzureResource'
      id: dbserver::db.id
    }
    authInfo: {
      authType: 'secret'
      name: 'postgresadmin'
      secretInfo: {
        secretType: 'rawValue'
        value: databasePassword
      }
    }
    secretStore: {
      keyVaultId: keyVault.id // Configure secrets as key vault references. No secret is exposed in App Service.
    }
    clientType: 'django'
  }
}

// Service Connector from the app to the cache, which generates an app setting for the App Service app
resource cacheConnector 'Microsoft.ServiceLinker/linkers@2024-04-01' = {
  scope: web
  name: 'RedisConnector'
  properties: {
    clientType: 'python'
    targetService: {
      type: 'AzureResource'
      id:  resourceId('Microsoft.Cache/Redis/Databases', redisCache.name, '0')
    }
    authInfo: {
      authType: 'accessKey'
    }
    secretStore: {
      keyVaultId: keyVault.id // Configure secrets as key vault references. No secret is exposed in App Service.
    }
    vNetSolution: {
      type: 'privateLink'
      
    }
  }
  dependsOn: [
    cachePrivateEndpoint
  ]
}

resource webdiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'AllLogs'
  scope: web
  properties: {
    workspaceId: logAnalyticsWorkspace.id
    logs: [
      {
        category: 'AppServiceHTTPLogs'
        enabled: true
      }
      {
        category: 'AppServiceConsoleLogs'
        enabled: true
      }
      {
        category: 'AppServiceAppLogs'
        enabled: true
      }
      {
        category: 'AppServiceAuditLogs'
        enabled: true
      }
      {
        category: 'AppServiceIPSecAuditLogs'
        enabled: true
      }
      {
        category: 'AppServicePlatformLogs'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${appName}-workspace'
  location: location
  tags: tags
  properties: any({
    retentionInDays: 30
    features: {
      searchVersion: 1
    }
    sku: {
      name: 'PerGB2018'
    }
  })
}

module applicationInsightsResources 'appinsights.bicep' = {
  name: 'applicationinsights-resources'
  params: {
    prefix: appName
    location: location
    tags: tags
    workspaceId: logAnalyticsWorkspace.id
  }
}

func checkAndFormatSecrets(config object) string => config.configType == 'KeyVaultSecret' ? '@Microsoft.KeyVault(SecretUri=${config.value})' : config.value

// Add the app settings, by merging them with the ones created by the service connectors
var aggregatedAppSettings = union(
  reduce(vaultConnector.listConfigurations().configurations, {}, (cur, next) => union(cur, { '${next.name}': checkAndFormatSecrets(next) })), 
  reduce(dbConnector.listConfigurations().configurations, {}, (cur, next) => union(cur, { '${next.name}': checkAndFormatSecrets(next) })), 
  reduce(cacheConnector.listConfigurations().configurations, {}, (cur, next) => union(cur, { '${next.name}': checkAndFormatSecrets(next) })), 
  {
    SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
    FLASK_DEBUG: 'False'
    SECRET_KEY: secretKey
    // Add other app settings here, for example:
    // 'FOO': 'BAR'
  }
)
resource appsettings 'Microsoft.Web/sites/config@2024-04-01' = {
  name: 'appsettings'
  parent: web
  properties: aggregatedAppSettings
}
// Why is this needed?
// The service connectors automatically add necessary respective app settings to the App Service app. However, if you configure a separate
// set of app settings in a config/appsettings resource, expecting a cummulative effect, the app settings actually overwrite the ones
// created by the service connectors, and the service connectors don't recreate the app settings after the first run. This configuration
// is a workaround to ensure that the app settings are aggregated correctly and consistent across multiple deployments.

output WEB_URI string = 'https://${web.properties.defaultHostName}'
output CONNECTION_SETTINGS array = map(concat(dbConnector.listConfigurations().configurations, cacheConnector.listConfigurations().configurations, vaultConnector.listConfigurations().configurations), config => config.name)
output APPLICATIONINSIGHTS_CONNECTION_STRING string = applicationInsightsResources.outputs.APPLICATIONINSIGHTS_CONNECTION_STRING
output WEB_APP_LOG_STREAM string = format('https://portal.azure.com/#@/resource{0}/logStream', web.id)
output WEB_APP_SSH string = format('https://{0}.scm.azurewebsites.net/webssh/host', web.name)
output WEB_APP_CONFIG string = format('https://portal.azure.com/#@/resource{0}/environmentVariablesAppSettings', web.id)
