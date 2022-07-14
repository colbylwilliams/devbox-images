packer {
  required_plugins {
    # https://github.com/rgl/packer-plugin-windows-update
    windows-update = {
      version = "0.14.1"
      source = "github.com/rgl/windows-update"
    }
  }
}

# https://www.packer.io/plugins/builders/azure/arm
source "azure-arm" "vm" {
  azure_tags = {
    branch = var.branch
    build  = timestamp()
    commit = var.commit
  }
  communicator                      = "winrm"
  winrm_username                    = "packer"
  winrm_insecure                    = true
  winrm_use_ssl                     = true
  image_publisher                   = "microsoftwindowsdesktop"
  image_offer                       = "windows-ent-cpc"
  image_sku                         = "win11-21h2-ent-cpc-m365"
  image_version                     = "latest"
  use_azure_cli_auth                = true
  managed_image_name                = var.image
  managed_image_resource_group_name = var.galleryResourceGroup
  location                          = var.location
  temp_resource_group_name          = var.tempResourceGroup
  build_resource_group_name         = var.buildResourceGroup
  user_assigned_managed_identities  = [var.identity]
  async_resourcegroup_delete        = true
  os_type                           = "Windows"
  vm_size                           = "Standard_D8s_v3"
  shared_image_gallery_destination {
    subscription         = var.subscription
    resource_group       = var.galleryResourceGroup
    gallery_name         = var.galleryName
    image_name           = var.image
    image_version        = var.version
    replication_regions  = var.replicaLocations
    storage_account_type = "Standard_LRS"
  }
}

build {
  sources = ["source.azure-arm.vm"]

  provisioner "powershell" {
    environment_vars  = [
      "ADMIN_USERNAME=${build.User}",
      "ADMIN_PASSWORD=${build.Password}" ]
    script            = "../../scripts/Enable-AutoLogon.ps1"
  }

  provisioner "windows-restart" {
    # needed to get elevated script execution working
    restart_timeout       = "30m"
    pause_before          = "2m"
  }

  # https://github.com/rgl/packer-plugin-windows-update
  provisioner "windows-update" {
  }

  provisioner "powershell" {
    elevated_user     = build.User
    elevated_password = build.Password
    script            = "../../scripts/Install-Chocolatey.ps1"
  }

  provisioner "powershell" {
    elevated_user     = build.User
    elevated_password = build.Password
    inline            = [
      "choco install postman --confirm",
      "choco install googlechrome --confirm",
      "choco install firefox --confirm"
    ]
  }

  provisioner "powershell" {
    elevated_user     = build.User
    elevated_password = build.Password
    scripts           = [
      "../../scripts/Install-DotNet.ps1",
      "../../scripts/Install-Python.ps1",
      "../../scripts/Install-GitHubDesktop.ps1",
      "../../scripts/Install-VSCode.ps1",
      "../../scripts/Install-AzureCLI.ps1",
      "../../scripts/Install-VS2022.ps1"
    ]
  }

  provisioner "powershell" {
    scripts = [
      "../../scripts/Disable-AutoLogon.ps1",
      "../../scripts/Generalize-VM.ps1"
    ]
  }
}
