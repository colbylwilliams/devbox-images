@description('Name for the container group')
param name string = 'colbygroupa'

@description('Location for all resources.')
param location string = resourceGroup().location

param container string = 'ghcr.io/colbylwilliams/devbox-images/builder'
param repository string = 'https://github.com/colbylwilliams/devbox-images.git'

param packerVars object = {}

var environmentVars = [for kv in items(packerVars): {
  name: 'PKR_VAR_${kv.key}'
  value: kv.value
}]

param images array = [
  'TestBox'
]

var storageName = take('s${toLower(name)}${uniqueString(resourceGroup().id)}', 24)

param identity string = '/subscriptions/e5f715ae-6c72-4a5c-87c8-495590c34828/resourcegroups/Identities/providers/Microsoft.ManagedIdentity/userAssignedIdentities/Contoso'

resource storage 'Microsoft.Storage/storageAccounts@2021-09-01' = {
  name: storageName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  resource fileServices 'fileServices' = {
    name: 'default'
    resource fileShare 'shares' = [for image in images: {
      name: toLower(image)
    }]
  }
}

resource group 'Microsoft.ContainerInstance/containerGroups@2021-10-01' = [for image in images: {
  name: image
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity}': {}
    }
  }
  properties: {
    containers: [
      {
        name: name
        properties: {
          image: container
          ports: [
            {
              port: 80
              protocol: 'TCP'
            }
          ]
          resources: {
            requests: {
              cpu: 1
              memoryInGB: 2
            }
          }
          volumeMounts: [
            {
              name: 'repo'
              mountPath: '/mnt/repo'
              readOnly: false
            }
            {
              name: 'storage'
              mountPath: '/mnt/storage'
              readOnly: false
            }
          ]
          environmentVariables: empty(packerVars) ? [
            {
              name: 'BUILD_IMAGE_NAME'
              value: image
            }
          ] : concat(
            [
              {
                name: 'BUILD_IMAGE_NAME'
                value: image
              }
            ], environmentVars
          )
        }
      }
    ]
    osType: 'Linux'
    restartPolicy: 'Never'
    ipAddress: {
      type: 'Public'
      ports: [
        {
          port: 80
          protocol: 'TCP'
        }
      ]
    }
    volumes: [
      {
        name: 'repo'
        gitRepo: {
          repository: repository
          directory: '.'
          revision: 'main'
        }
      }
      {
        name: 'storage'
        azureFile: {
          shareName: toLower(image)
          storageAccountName: storageName
          storageAccountKey: storage.listKeys().keys[0].value
          readOnly: false
        }
      }
    ]
  }
}]

// output containerIPv4Address string = group.properties.ipAddress.ip
// https://github.com/Azure/azure-quickstart-templates/blob/master/quickstarts/microsoft.containerinstance/aci-vnet/main.bicep
