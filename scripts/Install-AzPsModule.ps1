# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# Set TLS1.2
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor "Tls12"

# # The correct Modules need to be saved in C:\Modules
# $installPSModulePath = "C:\\Modules"
# if (-not (Test-Path -LiteralPath $installPSModulePath))
# {
#     Write-Host "Creating ${installPSModulePath} folder to store PowerShell Azure modules..."
#     $null = New-Item -Path $installPSModulePath -ItemType Directory
# }

Write-Host "Installing AZ PowerShell module..."
Install-Module -Name Az -Scope AllUsers -SkipPublisherCheck -Force
