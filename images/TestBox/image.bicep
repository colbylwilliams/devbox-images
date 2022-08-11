param name string
param location string = resourceGroup().location

param gallery object

param replicaLocations array

param version string

// param subnetId string

param identity string = '/subscriptions/e5f715ae-6c72-4a5c-87c8-495590c34828/resourcegroups/Identities/providers/Microsoft.ManagedIdentity/userAssignedIdentities/Contoso'

param source object = {
  type: 'PlatformImage'
  publisher: 'microsoftwindowsdesktop'
  offer: 'windows-ent-cpc'
  sku: 'win11-21h2-ent-cpc-m365'
  version: 'latest'
}

// param scriptsRepo object = {
//   org: 'Azure'
//   name: 'dev-box-images'
// }

// var scriptsRoot = 'https://raw.githubusercontent.com/${scriptsRepo.org}/${scriptsRepo.name}/main/scripts'

param tempResourceGroup string = ''
param buildResourceGroup string = ''

var resolvedResourceGroupName = empty(buildResourceGroup) ? empty(tempResourceGroup) ? '' : tempResourceGroup : buildResourceGroup
var stagingResourceGroup = empty(resolvedResourceGroupName) ? '' : '${subscription().id}/resourceGroups/${resolvedResourceGroupName}'

resource gal 'Microsoft.Compute/galleries@2022-01-03' existing = {
  name: gallery.name
  scope: resourceGroup(gallery.resourceGroup)
}

resource definition 'Microsoft.Compute/galleries/images@2022-01-03' existing = {
  name: name
  parent: gal
}

resource template 'Microsoft.VirtualMachineImages/imageTemplates@2022-02-14' = {
  name: name
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity}': {}
    }
  }
  properties: {
    // buildTimeoutInMinutes: 120 // seems to need more than 2 hours (default is 4 hours)
    stagingResourceGroup: stagingResourceGroup
    vmProfile: {
      vmSize: 'Standard_D8s_v3'
      // userAssignedIdentities:
      // vnetConfig: {
      //   subnetId: subnetId
      // }
    }
    source: source
    distribute: [
      {
        type: 'SharedImage'
        galleryImageId: '${definition.id}/versions/${version}'
        runOutputName: '${name}-${version}-SI'
        replicationRegions: replicaLocations
        storageAccountType: 'Standard_LRS'
      }
    ]
    customize: [
      {
        type: 'PowerShell'
        inline: [
          'Write-Host "Hello World!"'
        ]
      }
    ]
  }
}
