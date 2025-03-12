import asyncio
import aiohttp
from typing import List, Dict, Any
from langflow.custom import Component
from langflow.inputs.inputs import DataInput, MessageTextInput
from langflow.io import Output
from langflow.schema import Data, Message


class DownloadFilesContentComponent(Component):
    """Component for downloading file content from DocSpace via API."""


    display_name: str = "Download Files"
    description: str = "Downloads file content from DocSpace using viewUrl, retrieving binary content and metadata including content type, size, and version"
    name: str = "DownloadFiles"
    icon = "file-download"

    inputs = [
        DataInput(
            name="files_info",
            display_name="Files Info",
            info="List of file information to download",
            required=True,
        ),
        MessageTextInput(
            name="asc_auth_key",
            display_name="Auth key",
            info="Auth key to use",
            required=True,
        )
    ]

    outputs = [
        Output(
            name="files",
            display_name="Files",
            method="download_files",
        ),
    ]

    async def download_file(self, session: aiohttp.ClientSession, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Download a single file using async HTTP request.

        Args:
            session: aiohttp client session
            file_info: Dictionary containing file information

        Returns:
            Dictionary with file content and metadata
        """
        try:
            headers = {
                'Authorization': self.asc_auth_key,
            }

            download_url = file_info.get('viewUrl')
            if not download_url:
                raise ValueError(f"Missing viewUrl in file info: {file_info}")

            async with session.get(download_url, headers=headers, timeout=30) as response:
                response.raise_for_status()
                content = await response.read()
                content_type = response.headers.get('content-type', '')

                return {
                    'content': content,
                    'content_type': content_type,
                    'extension': file_info.get('fileExst', '').lower(),
                    'title': file_info.get('title', ''),
                    'version': file_info.get('version', ''),
                    'id': file_info.get('id', ''),
                    'size': len(content)
                }

        except Exception as e:
            print(
                f"Error downloading file {file_info.get('id', 'unknown')}: {str(e)}")
            return None

    async def fetch_all_files(self, files_info: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Download all files concurrently using aiohttp.

        Args:
            files_info: List of file information dictionaries

        Returns:
            List of dictionaries with file contents and metadata
        """
        async with aiohttp.ClientSession() as session:
            # Create tasks for all file downloads
            tasks = [self.download_file(session, file_info)
                     for file_info in files_info]
            # Wait for all tasks to complete (like Promise.all)
            results = await asyncio.gather(*tasks)
            # Filter out None results (failed downloads)
            return [r for r in results if r is not None]

    async def download_files(self) -> Data:
        """
        Download multiple files concurrently.

        Returns:
            Data object containing downloaded files
        """
        try:
            # Get files info from input
            files_data = self.files_info
            if not isinstance(files_data, Data) or not files_data.data:
                return Data(data={"files": []})

            files_info = files_data.data.get("files", [])
            if not files_info:
                return Data(data={"files": []})

            # Download all files concurrently
            downloaded_files = await self.fetch_all_files(files_info)
            return Data(data={"files": downloaded_files})

        except Exception as e:
            raise ValueError(f"Error downloading files: {str(e)}")
