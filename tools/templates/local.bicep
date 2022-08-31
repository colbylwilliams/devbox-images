// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

targetScope = 'subscription'

param base string
param location string = 'eastus'
param builderPrincipalId string = 'd6d89d7c-5a1a-4abb-b086-f74ce033c073'
param tags object = {}

var builderIpPrefix = '10.6'

resource group_dc 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${base}-dev'
  location: location
}

resource group_net 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${base}-net'
  location: location
}

resource group_gal 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${base}-gallery'
  location: location
}

resource group_images 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${base}-images'
  location: location
}

module devcenter 'devcenter.bicep' = {
  scope: group_dc
  name: '${base}-devcenter'
  params: {
    name: base
    location: location
    tags: tags
  }
}

module gallery 'gallery.bicep' = {
  scope: group_gal
  name: '${base}-gallery'
  params: {
    name: base
    location: location
    devCenterId: devcenter.outputs.id
    builderPrincipalId: builderPrincipalId
    tags: tags
  }
}

module vnet 'vnet.bicep' = {
  scope: group_net
  name: '${base}-vnet'
  params: {
    name: '${base}-vnet'
    location: location
    tags: tags
  }
}

module vnet_nc 'networkConnection.bicep' = {
  scope: group_net
  name: '${base}-vnet-nc'
  params: {
    name: '${base}-vnet-nc'
    location: location
    devCenterId: devcenter.outputs.id
    vnetId: vnet.outputs.id
    subnet: vnet.outputs.subnet
    networkingResourceGroupName: '${group_net.name}-nc'
    tags: tags
  }
}

module builder '../../builder/templates/builder_sandbox.bicep' = {
  scope: group_images
  name: '${base}-builder'
  params: {
    baseName: '${base}-img'
    location: location
    vnetAddressPrefixes: [ '${builderIpPrefix}.0.0/16' ]
    defaultSubnetName: 'default'
    defaultSubnetAddressPrefix: '${builderIpPrefix}.0.0/27'
    builderSubnetName: 'builders'
    builderSubnetAddressPrefix: '${builderIpPrefix}.1.0/27'
    builderPrincipalId: builderPrincipalId
    tags: tags
  }
}

module project 'project.bicep' = {
  scope: group_dc
  name: '${base}-project'
  params: {
    name: '${base}-proj'
    location: location
    devCenterId: devcenter.outputs.id
    projectAdmins: [ 'e40cb79e-413f-4c73-9ce1-7fbf52f33841' ]
    devBoxUsers: [ '7c4f654c-1755-41d6-b907-a35d470f9086' ]
    tags: tags
  }
}
