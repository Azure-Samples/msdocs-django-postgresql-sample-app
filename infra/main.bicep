targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name which is used to generate a short unique hash for each resource')
param name string

@minLength(1)
@description('Primary location for all resources')
param location string

@secure()
@description('PostGreSQL Server administrator password')
param databasePassword string

@secure()
@description('Django SECRET_KEY for securing signed data')
param secretKey string

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var tags = { 'azd-env-name': name }

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${name}-rg'
  location: location
  tags: tags
}

module resources 'resources.bicep' = {
  name: 'resources'
  scope: resourceGroup
  params: {
    name: name
    location: location
    resourceToken: resourceToken
    tags: tags
    databasePassword: databasePassword
    secretKey: secretKey
  }
}

output AZURE_LOCATION string = location
output APPLICATIONINSIGHTS_CONNECTION_STRING string = resources.outputs.APPLICATIONINSIGHTS_CONNECTION_STRING
output WEB_URI string = resources.outputs.WEB_URI
output WEB_APP_SETTINGS array = resources.outputs.WEB_APP_SETTINGS
output WEB_APP_LOG_STREAM string = resources.outputs.WEB_APP_LOG_STREAM
output WEB_APP_SSH string = resources.outputs.WEB_APP_SSH
output WEB_APP_CONFIG string = resources.outputs.WEB_APP_CONFIG