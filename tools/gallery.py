import os
from pathlib import Path

import syaml

this_path = Path(__file__).resolve().parent
repo_root = this_path.parent


def get():
    gallery_yaml = os.path.isfile(os.path.join(repo_root, 'gallery.yaml'))
    gallery_yml = os.path.isfile(os.path.join(repo_root, 'gallery.yml'))

    if not gallery_yaml and not gallery_yml:
        raise ValueError('gallery.yaml or gallery.yml not found in the root of the repository')

    if gallery_yaml and gallery_yml:
        raise ValueError("found both 'gallery.yaml' and 'gallery.yml' in root of repository. only one gallery yaml file allowed")

    gallery_path = repo_root / 'gallery.yaml' if gallery_yaml else repo_root / 'gallery.yml'

    gallery = syaml.parse(gallery_path)

    if 'name' not in gallery or not gallery['name']:
        raise ValueError("gallery.yaml/gallery.yml must have a 'name' property with a value")

    if 'resourceGroup' not in gallery or not gallery['resourceGroup']:
        raise ValueError("gallery.yaml/gallery.yml must have a 'resourceGroup' property with a value")

    return gallery
