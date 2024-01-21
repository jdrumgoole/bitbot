import click
import aiofiles
import asyncio
import fnmatch
import hashlib
import httpx
from pathlib import Path

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
        'file': (file_path.name, content),
        'checksum': (None, checksum),
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, files=files)
    return response

async def find_and_upload_files(directory, include_filter, exclude_filter, url):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if fnmatch.fnmatch(file, include_filter) and not fnmatch.fnmatch(file, exclude_filter):
                file_path = Path(root) / file
                checksum = await calculate_sha256_async(file_path)
                response = await upload_file_async(url, file_path, checksum)
                if response.status_code == 200:
                    click.echo(f"Successfully uploaded {file_path}")
                else:
                    click.echo(f"Failed to upload {file_path}. Status code: {response.status_code}, Detail: {response.text}")

@click.command()
@click.option('--path', default=str(Path.home()), help='Directory path to search for files.', show_default=True)
@click.option('--includefilter', default='*', help='Glob pattern to include files.', show_default=True)
@click.option('--excludefilter', default='', help='Glob pattern to exclude files.', show_default=True)
@click.option('--url', required=True, help='URL of the FastAPI upload endpoint.')
def main(path, includefilter, excludefilter, url):
    asyncio.run(find_and_upload_files(path, includefilter, excludefilter, url))

if __name__ == '__main__':
    main()
bitbot