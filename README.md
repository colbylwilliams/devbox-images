# Dev Box Images

This repo contains custom images to be used with [Microsoft Dev Box](https://techcommunity.microsoft.com/t5/azure-developer-community-blog/introducing-microsoft-dev-box/ba-p/3412063).  It demonstrates how to create custom images with pre-installed software using [Packer](https://www.packer.io/) and shared them via [Azure Compute Gallery](https://docs.microsoft.com/en-us/azure/virtual-machines/shared-image-galleries).

See the [workflow file](https://github.com/colbylwilliams/devbox-images/blob/main/.github/workflows/build_images.yml) to see how images are built and deployed.

## Images

[![Build Images](https://github.com/colbylwilliams/devbox-images/actions/workflows/build_images.yml/badge.svg)](https://github.com/colbylwilliams/devbox-images/actions/workflows/build_images.yml)

| Name      | OS                             | Additional Software                                          |
| --------- | ------------------------------ | -------------------------------------------------------------|
| VS2022Box | [Windows 11 Enterprise][win11] | [Visual Studio 2022](https://visualstudio.microsoft.com/vs/) |
| VSCodeBox | [Windows 11 Enterprise][win11] |                                                              |

Use [this form](https://github.com/colbylwilliams/devbox-images/issues/new?assignees=colbylwilliams&labels=image&template=request_image.yml&title=%5BImage%5D%3A+) to request a new image.

### Preinstalled Software

The following software is installed on all images. Use [this form](https://github.com/colbylwilliams/devbox-images/issues/new?assignees=colbylwilliams&labels=software&template=request_software.yml&title=%5BSoftware%5D%3A+) to request additional software.

- [Microsoft 365 Apps](https://www.microsoft.com/en-us/microsoft-365/products-apps-services)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Google Chrome](https://www.google.com/chrome/)
- [Firefox](https://www.mozilla.org/en-US/firefox/new/)
- [GitHub Desktop](https://desktop.github.com/)
- [Postman](https://www.postman.com/)
- [Chocolatey](https://chocolatey.org/)
- [.Net](https://dotnet.microsoft.com/en-us/) (versions 3.1, 5.0, 6.0, 7.0)
- [Python](https://www.python.org/) (version 3.10.5)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/what-is-azure-cli) (2.37.0)

## Usage

To get started:

1. Fork this repository
2. In your fork create a new [repository secret](https://docs.github.com/en/actions/reference/encrypted-secrets#creating-encrypted-secrets-for-a-repository) named `AZURE_CREDENTIALS` with a value that contains credentials for a service principal with appropriate permissions to create resource groups and deploy images to an [Azure Compute Gallery](https://docs.microsoft.com/en-us/azure/virtual-machines/shared-image-galleries?tabs=azure-cli). For details on how to create these credentials, see the [Azure Login action docs](https://github.com/Azure/login#configure-deployment-credentials).
3. Open the `build_images.yml` file and update the environment variables: [`galleryName`](https://github.com/colbylwilliams/devbox-images/blob/main/.github/workflows/build_images.yml#L4) and [`resourceGroup`](https://github.com/colbylwilliams/devbox-images/blob/main/.github/workflows/build_images.yml#L5) to match your Azure Compute Gallery.

**Important: when pasting in the value for `AZURE_CREDENTIALS`, remove all line breaks so that the JSON is on a single line. Otherwise GitHub will assume subscriptionId and tenantId are secrets and prevent them from being share across workflow jobs.**

Example:

```json
{ "clientId": "<GUID>", "clientSecret": "<GUID>", "subscriptionId": "<GUID>", "tenantId": "<GUID>" }
```

[win11]:https://www.microsoft.com/en-us/microsoft-365/windows/windows-11-enterprise
