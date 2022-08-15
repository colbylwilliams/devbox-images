// packer {
//   required_plugins {
//     # https://github.com/rgl/packer-plugin-windows-update
//     windows-update = {
//       version = "0.14.1"
//       source  = "github.com/rgl/windows-update"
//     }
//   }
// }

# https://www.packer.io/plugins/builders/azure/arm
source "azure-arm" "vm" {
  skip_create_image                = false
  user_assigned_managed_identities = var.identities # optional
  async_resourcegroup_delete       = true
  vm_size                          = "Standard_D8s_v3" # default is Standard_A1
  # winrm options
  communicator   = "winrm"
  winrm_username = "packer"
  winrm_insecure = true
  winrm_use_ssl  = true
  os_type        = "Windows" # tells packer to create a certificate for WinRM connection
  # base image options (Azure Marketplace Images only)
  image_publisher    = "microsoftwindowsdesktop"
  image_offer        = "windows-ent-cpc"
  image_sku          = "win11-21h2-ent-cpc-m365"
  image_version      = "latest"
  use_azure_cli_auth = true
  # managed image options
  managed_image_name                = var.name
  managed_image_resource_group_name = var.gallery.resourceGroup
  # packer creates a temporary resource group
  location                 = var.location
  temp_resource_group_name = var.tempResourceGroup
  # OR use an existing resource group
  build_resource_group_name = var.buildResourceGroup
  # optional use an existing key vault
  build_key_vault_name = var.keyVault
  # optional use an existing virtual network
  virtual_network_name                = var.virtualNetwork
  virtual_network_subnet_name         = var.virtualNetworkSubnet
  virtual_network_resource_group_name = var.virtualNetworkResourceGroup
  shared_image_gallery_destination {
    subscription         = var.subscription
    gallery_name         = var.gallery.name
    resource_group       = var.gallery.resourceGroup
    image_name           = var.name
    image_version        = var.version
    replication_regions  = var.replicaLocations
    storage_account_type = "Standard_LRS" # default is Standard_LRS
  }
}

build {
  sources = ["source.azure-arm.vm"]

  provisioner "powershell" {
    inline = [
      "Write-Host 'Hello World!'",
    ]
  }
}
