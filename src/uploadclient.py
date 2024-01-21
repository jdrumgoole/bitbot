import click
import os
import fnmatch
import hashlib
import requests
from pathlib import Path

def calculate_sha256(file_path):
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def upload_file(url, file_path, checksum):
    with open(file_path, 'rb') as f:
        files = {
            'file': (os.path.basename(file_path), f),
            'checksum': (None, checksum),
        }
        response = requests.post(url, files=files)
    return response

def find_files(directory, include_filter='*', exclude_filter=''):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if fnmatch.fnmatch(file, include_filter) and not fnmatch.fnmatch(file, exclude_filter):
                yield os.path.join(root, file)

@click.command()
@click.option('--path', default=str(Path.home()), help='Directory path to search for files.', show_default=True)
@click.option('--includefilter', default='*', help='Glob pattern to include files.', show_default=True)
@click.option('--excludefilter', default='', help='Glob pattern to exclude files.', show_default=True)
@click.option('--url', required=True, help='URL of the FastAPI upload endpoint.')
@click.option('--quiet', is_flag=True, default=False, help='Suppress all but error output.')

def upload_files(path, includefilter, excludefilter, url, quiet):
    """This program uploads files from a given directory to a FastAPI server,
    applying include and exclude filters, and sends a SHA-256 checksum for validation."""
    verbose = not quiet
    for file_path in find_files(path, includefilter, excludefilter):
        checksum = calculate_sha256(file_path)
        response = upload_file(url, file_path, checksum)
        if response.status_code == 200:
            if verbose:
                click.echo(f"OK {response.text}")
        else:
            click.echo(f"Failed to upload {file_path}. Status code: {response.status_code}, Detail: {response.text}")

if __name__ == '__main__':
    upload_files()
