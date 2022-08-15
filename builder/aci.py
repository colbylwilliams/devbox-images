import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import azure
import build
import gallery
import images
import loggers

in_builder = os.environ.get('ACI_IMAGE_BUILDER', False)
in_builder = True if in_builder else False

log = loggers.getLogger(__name__)

log.info(f'ACI_IMAGE_BUILDER: {in_builder}')
log.debug(f'in_builder: {in_builder}')


def error_exit(message):
    log.error(message)
    sys.exit(message)


def main(imgs, run_build, suffix):
    for img in imgs:

        build, imgdef = azure.ensure_image_def_version(img)
        img['build'] = build

        # if buildResourceGroup is not provided we'll provide a name and location for the resource group
        if 'buildResourceGroup' not in img or not img['buildResourceGroup']:
            img['location'] = imgdef['location']
            img['tempResourceGroup'] = f'{img["gallery"]["name"]}-{img["name"]}-{suffix}'

    build_imgs = [i for i in imgs if i['build']]

    for img in build_imgs:

        params = {
            '$schema': 'https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#',
            'contentVersion': '1.0.0.0',
            'parameters': {}
        }

        params['parameters']['image'] = {
            'value': img['name']
        }

        with open(Path(img['path']) / 'builder.parameters.json', 'w') as f:
            json.dump(params, f, ensure_ascii=False, indent=4, sort_keys=True)

        if run_build:
            bicep_file = os.path.join(Path(__file__).resolve().parent, 'builder2.bicep')
            params_file = '@' + os.path.join(img['path'], 'builder.parameters.json')

            if 'tempResourceGroup' in img and img['tempResourceGroup']:
                group_name = img['tempResourceGroup']
                group = azure.cli(['group', 'create', '-n', img['tempResourceGroup'], '-l', img['location']])
            else:
                group_name = img['buildResourceGroup']

            group = azure.cli(['deployment', 'group', 'create', '-n', img['name'], '-g', group_name, '-f', bicep_file, '-p', params_file, '--no-prompt'])

        # params['parameters']['images'] = [i['name'] for i in build_imgs]
    if not run_build:
        log.warning('skipping build execution because --build | -b was not provided')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Build custom images for Microsoft Dev Box using Packer then pubish them to an Azure Compute Gallery.'
                                     'This script asumes the presence of a gallery.yaml file in the root of the repository and image.yaml files in each subdirectory of the /images directory',
                                     epilog='example: python3 aci.py --suffix 22 --build')
    parser.add_argument('--images', '-i', nargs='*', help='names of images to build. if not specified all images will be')
    parser.add_argument('--changes', '-c', nargs='*', help='paths of the files that changed to determine which images to build. if not specified all images will be built')
    parser.add_argument('--suffix', '-s', help='suffix to append to the resource group name. if not specified, the current time will be used')
    parser.add_argument('--build', '-b', dest='run_build', action='store_true', help='build images with packer or azure image builder depening on the builder property in the image definition yaml')

    args = parser.parse_args()

    # is_async = args.is_async
    run_build = args.run_build

    suffix = args.suffix if args.suffix else datetime.now(timezone.utc).strftime('%Y%m%d%H%M')

    gal = gallery.get()
    imgs = [images.get(i) for i in args.images] if args.images else images.all()

    for img in imgs:
        img['gallery'] = gal

    # if is_async:
    #     asyncio.run(main_async(imgs, run_build, suffix))
    # else:
    main(imgs, run_build, suffix)
