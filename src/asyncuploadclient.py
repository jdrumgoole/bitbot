import click
import aiofiles
import asyncio
import fnmatch
import hashlib
import httpx
import os
from pathlib import Path

verbose = True  # Global variable to control verbosity

async def calculate_sha256_async(file_path):
    hash_sha256 = hashlib.sha256()
    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(4096):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

async def upload_file_async(url, file_path, checksum):
    async with aiofiles.open(file_path, 'rb') as f:
        content = await f.read()
    files = {
        'file': (os.path.basename(file_path), content),
        'checksum': (None, checksum),
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, files=files)
    return response, file_path, response.status_code

async def process_file(url, file_path, include_filter, exclude_filter):
    if fnmatch.fnmatch(file_path.name, include_filter) and not fnmatch.fnmatch(file_path.name, exclude_filter):
        checksum = await calculate_sha256_async(file_path)
        response, path, status_code = await upload_file_async(url, file_path, checksum)
        if status_code == 200:
            if verbose:
                click.echo(f"Successfully uploaded {path}")
        else:
            click.echo(f"Failed to upload {path}. Status code: {status_code}, Detail: {response.text}")

async def find_and_upload_files(directory, include_filter, exclude_filter, url, concurrency):
    tasks = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            tasks.append(process_file(url, file_path, include_filter, exclude_filter))
            if len(tasks) >= concurrency:
                await asyncio.gather(*tasks)
                tasks = []
    if tasks:  # Process any remaining tasks
        await asyncio.gather(*tasks)

@click.command()
@click.option('--path', default=str(Path.home()), help='Directory path to search for files.', show_default=True)
@click.option('--includefilter', default='*', help='Glob pattern to include files.', show_default=True)
@click.option('--excludefilter', default='', help='Glob pattern to exclude files.', show_default=True)
@click.option('--url', required=True, help='URL of the FastAPI upload endpoint.')
@click.option('--quiet', is_flag=True, help='Suppress all but error output.')
@click.option('--concurrency', default=10, help='Maximum number of files to process in parallel.', show_default=True)
def main(path, includefilter, excludefilter, url, quiet, concurrency):
    global verbose
    verbose = not quiet
    asyncio.run(find_and_upload_files(path, includefilter, excludefilter, url, concurrency))

if __name__ == '__main__':
    main()
