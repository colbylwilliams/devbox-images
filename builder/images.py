import argparse
import os
import sys
from pathlib import Path

import loggers
import syaml

in_builder = os.environ.get('ACI_IMAGE_BUILDER', False)
is_github = os.environ.get('GITHUB_ACTIONS', False)

repo = Path('/mnt/repo') if in_builder else Path(__file__).resolve().parent.parent
images_root = repo / 'images'

required_properties = ['publisher', 'offer', 'sku', 'version', 'os', 'replicaLocations', 'builder']

log = loggers.getLogger(__name__)


def error_exit(message):
    log.error(message)
    sys.exit(message)


def validate(image):
    log.info(f'validating image {image["name"]}')
    for required_property in required_properties:
        if required_property not in image:
            error_exit(f'image.yaml for {image["name"]} is missing required property {required_property}')
        if not image[required_property]:
            error_exit(f'image.yaml for {image["name"]} is missing a value for required property {required_property}')
    if image['builder'] not in ['packer', 'azure']:
        error_exit(f'image.yaml for {image["name"]} has an invalid builder property value {image["builder"]}')


def get(image_name) -> dict:
    '''
    ### Summary
    Looks for a directory containing a 'image.yaml' or 'image.yml' file in the /images direcory and returns a dictionary of the contents.

    ### Returns:
    A dictionary of the contents of the image.yaml file.
    '''
    image_dir = images_root / image_name
    log.info(f'Getting image {image_name} from {image_dir}')

    if not os.path.isdir(image_dir):
        error_exit(f'Directory for image {image_name} not found at {image_dir}')

    image_yaml = os.path.isfile(os.path.join(image_dir, 'image.yaml'))
    image_yml = os.path.isfile(os.path.join(image_dir, 'image.yml'))

    if not image_yaml and not image_yml:
        error_exit(f'image.yaml or image.yml not found {image_dir}')

    if image_yaml and image_yml:
        error_exit(f"Found both 'image.yaml' and 'image.yml' in {image_dir} of repository. only one image yaml file allowed")

    image_path = image_dir / 'image.yaml' if image_yaml else image_dir / 'image.yml'

    image = syaml.parse(image_path)
    image['name'] = Path(image_dir).name
    image['path'] = f'{image_dir}'

    if 'builder' in image and image['builder']:
        if image['builder'].lower() in ['az', 'azure', 'aib', 'azureimagebuilder' 'azure-image-builder', 'imagebuilder', 'image-builder']:
            image['builder'] = 'azure'
        elif image['builder'].lower() in ['packer', 'pkr']:
            image['builder'] = 'packer'
    else:
        image['builder'] = 'packer'

    validate(image)

    return image


def all() -> list:
    '''
    ### Summary
    Looks for a directories containing a 'image.yaml' or 'image.yml' file in the /images direcory and returns a list of dictionaries of the contents.

    ### Returns:
    A list of dictionaries with the contents of the image.yaml files.
    '''
    images = []

    # walk the images directory and find all the image.yml/image.yaml files
    for dirpath, dirnames, files in os.walk(images_root):
        # os.walk includes the root directory (i.e. repo/images) so we need to skip it
        if not images_root.samefile(dirpath) and Path(dirpath).parent.samefile(images_root):
            image = get(Path(dirpath).name)
            images.append(image)

    return images


def main(images):
    import json
    imgs = [get(i) for i in images] if images else all()

    if is_github:
        print("::set-output name=images::{}".format(json.dumps({'include': imgs})))
        print("::set-output name=build::{}".format(len(imgs) > 0))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='generates the matrix for fan out builds in github actions.')
    parser.add_argument('--images', '-i', nargs='*', help='names of images to include. if not specified all images will be')

    args = parser.parse_args()

    main(args.images)
