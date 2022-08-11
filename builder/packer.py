import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import azure
import loggers

is_github = os.environ.get('GITHUB_ACTIONS', False)
in_builder = os.environ.get('ACI_IMAGE_BUILDER', False)

repo = Path('/mnt/repo') if in_builder else Path(__file__).resolve().parent.parent
images_root = repo / 'images'

default_pkr_vars = [
    'subscription',
    'name',
    'location',
    'version',
    'tempResourceGroup',
    'buildResourceGroup',
    'gallery',
    'replicaLocations',
    'repos',
    'branch',
    'commit'
]

log = loggers.getLogger(__name__)


def error_exit(message):
    log.error(message)
    sys.exit(message)


def _parse_command(command):
    if isinstance(command, list):
        args = command
    elif isinstance(command, str):
        args = command.split()
    else:
        raise ValueError(f'command must be a string or list, not {type(command)}')

    packer = shutil.which('packer')

    if args[0] == 'packer':
        args.pop(0)

    if args[0] != packer:
        args = [packer] + args

    return args


def get_vars(image):
    try:
        args = _parse_command(['inspect', '-machine-readable', image['path']])
        log.info(f'Running packer command: {" ".join(args)}')
        proc = subprocess.run(args, capture_output=True, check=True, text=True)
        if proc.stdout:
            log.info(f'\n\n{proc.stdout}')
            return [v.strip().split('var.')[1].split(':')[0] for v in proc.stdout.split('\\n') if v.startswith('var.')]
        return default_pkr_vars
    except subprocess.CalledProcessError:
        return default_pkr_vars


async def get_vars_async(image):
    try:
        args = _parse_command(['inspect', '-machine-readable', image['path']])
        proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if stdout:
            log.info(f'\n\n{stdout}')
            return [v.strip().split('var.')[1].split(':')[0] for v in stdout.decode().split('\\n') if v.startswith('var.')]
        return default_pkr_vars
    except subprocess.CalledProcessError:
        return default_pkr_vars


def save_vars_file(image, sub=None):
    sub = sub if sub else azure.get_sub()

    pkr_vars = get_vars(image)

    auto_vars = {
        'subscription': sub,
    }

    for v in pkr_vars:
        if v in image and image[v]:
            auto_vars[v] = image[v]

    with open(Path(image['path']) / 'vars.auto.pkrvars.json', 'w') as f:
        json.dump(auto_vars, f, ensure_ascii=False, indent=4, sort_keys=True)


async def save_vars_file_async(image, sub=None):
    sub = sub if sub else await azure.get_sub_async()

    pkr_vars = await get_vars_async(image)

    auto_vars = {
        'subscription': sub,
    }

    for v in pkr_vars:
        if v in image and image[v]:
            auto_vars[v] = image[v]

    with open(Path(image['path']) / 'vars.auto.pkrvars.json', 'w') as f:
        json.dump(auto_vars, f, ensure_ascii=False, indent=4, sort_keys=True)


def save_vars_files(images):
    sub = azure.get_sub()

    for image in images:
        save_vars_file(image, sub)


def init(image):
    log.info(f'Executing packer init for {image["name"]}')
    args = _parse_command(['init', image['path']])
    log.info(f'Running packer command: {" ".join(args)}')
    proc = subprocess.run(args, capture_output=True, check=True, text=True)
    log.info(f'\n\n{proc.stdout}')
    log.info(f'Done executing packer init for {image["name"]}')
    return proc.returncode


async def init_async(image):
    log.info(f'Executing packer init for {image["name"]}')
    args = _parse_command(['init', image['path']])
    log.info(f'Running packer command: {" ".join(args)}')
    proc = await asyncio.create_subprocess_exec(*args)
    stdout, stderr = await proc.communicate()
    # log.info(f'\n\n{stdout}')
    log.info(f'Done executing packer init for {image["name"]}')
    log.info(f'[packer init for {image["name"]} exited with {proc.returncode}]')
    return proc.returncode


def build(image):
    log.info(f'Executing packer build for {image["name"]}')
    args = _parse_command(['build', '-force', image['path']])
    if in_builder:
        args.append('-color=false')
    log.info(f'Running packer command: {" ".join(args)}')
    proc = subprocess.run(args, capture_output=True, check=True, text=True)
    log.info(f'\n\n{proc.stdout}')
    log.info(f'Done executing packer build for {image["name"]}')
    return proc.returncode


async def build_async(image):
    log.info(f'Executing packer build for {image["name"]}')
    args = _parse_command(['build', '-force', image['path']])
    if in_builder:
        args.append('-color=false')
    log.info(f'Running packer command: {" ".join(args)}')
    proc = await asyncio.create_subprocess_exec(*args)
    stdout, stderr = await proc.communicate()
    # log.info(f'\n\n{stdout}')
    log.info(f'Done executing packer build for {image["name"]}')
    log.info(f'[packer build for {image["name"]} exited with {proc.returncode}]')
    return proc.returncode


def execute(image):
    i = init(image)
    return build(image) if i == 0 else i


async def execute_async(image):
    i = await init_async(image)
    return await build_async(image) if i == 0 else i


def main(img_name):
    img_dir = images_root / img_name

    if not os.path.isdir(img_dir):
        error_exit(f'Directory for image {img_name} not found at {img_dir}')

    if not os.path.isfile(img_dir / 'vars.auto.pkrvars.json'):
        error_exit(f'vars.auto.pkrvars.json not found in {img_dir} must execute build.py first')

    image = {}
    image['name'] = Path(img_dir).name
    image['path'] = f'{img_dir}'

    execute(image)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='builds a single image. assumes the image is already using the build.py without the --packer | -p arg.')
    parser.add_argument('--image', '-i', required=True, help='name of the image to build')

    args = parser.parse_args()

    img_name = args.image
    main(img_name)
