

import json

test1 = 'https://github.com/colbylwilliams/devbox-images.git'
test2 = 'git@github.com:colbylwilliams/devbox-images.git'
test3 = 'https://dev.azure.com/colbylwilliams/MyProject/_git/devbox-images'
test4 = 'https://colbylwilliams.visualstudio.com/DefaultCollection/MyProject/_git/devbox-images'
test5 = 'https://colbylwilliams@dev.azure.com/colbylwilliams/MyProject/_git/devbox-images'


def _is_github(url) -> bool:
    return 'github.com' in url.lower()


def _is_devops(url) -> bool:
    return 'dev.azure.com' in url.lower() or 'visualstudio.com' in url.lower()


def _parse_github_url(url) -> dict:
    # examples:
    # https://github.com/colbylwilliams/devbox-images.git
    # git@github.com:colbylwilliams/devbox-images.git

    if not _is_github(url):
        raise ValueError(f'{url} is not a valid GitHub repository url')

    url = url.lower().replace('git@', 'https://').replace('github.com:', 'github.com/')

    if url.endswith('.git'):
        url = url[:-4]

    parts = url.split('/')

    index = next((i for i, part in enumerate(parts) if 'github.com' in part), -1)

    if index == -1 or len(parts) < index + 3:
        raise ValueError(f'{url} is not a valid GitHub repository url')

    repo = {
        'provider': 'github',
        'url': url,
        'org': parts[index + 1],
        'repo': parts[index + 2],
        'gitUrl': f'{url}.git',
    }

    return repo


def _parse_devops_url(url) -> dict:
    # examples:
    # https://dev.azure.com/colbylwilliams/MyProject/_git/devbox-images
    # https://colbylwilliams.visualstudio.com/DefaultCollection/MyProject/_git/devbox-images
    # https://colbylwilliams@dev.azure.com/colbylwilliams/MyProject/_git/devbox-images

    if not _is_devops(url):
        raise ValueError(f'{url} is not a valid Azure DevOps respository url')

    url = url.lower().replace('git@ssh', 'https://').replace(':v3/', '/')

    if url.endswith('.git'):
        url = url[:-4]

    parts = url.split('/')

    index = next((i for i, part in enumerate(parts) if 'dev.azure.com' in part or 'visualstudio.com' in part), -1)

    if index == -1:
        raise ValueError(f'{url} is not a valid Azure DevOps respository url')

    if '_git' in parts:
        parts.pop(parts.index('_git'))
    else:
        last = parts[-1]
        url = url.replace(f'/{last}', f'/_git/{last}')

    if 'dev.azure.com' in parts[index]:
        index += 1

    if len(parts) < index + 3:
        raise ValueError(f'{url} is not a valid Azure DevOps respository url')

    repo = {
        'provider': 'devops',
        'url': url,
        'org': parts[index].replace('visualstudio.com', ''),
        'project': parts[index + 1],
        'repo': parts[index + 2],
        'gitUrl': f'{url}.git'
    }

    return repo


def parse_url(url) -> dict:

    if _is_github(url):
        return _parse_github_url(url)

    if _is_devops(url):
        return _parse_devops_url(url)

    raise ValueError(f'{url} is not a valid repository url')


# print('')
# for test in [test1, test2, test3, test4, test5]:
#     repo = parse_url(test)
#     print(json.dumps(repo, indent=4))
#     print('')
