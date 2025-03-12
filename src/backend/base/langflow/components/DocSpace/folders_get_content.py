import asyncio
import aiohttp
from typing import List, Dict, Any
from langflow.custom import Component
from langflow.inputs.inputs import MessageInput, DataInput, MessageTextInput
from langflow.io import Output
from langflow.schema import Data


class GetFoldersContentComponent(Component):
    """Component for retrieving complete folder content from DocSpace via API."""

    display_name: str = "Get Folder Content"
    description: str = "Retrieves folder content including files, subfolders, and metadata from DocSpace"
    name: str = "GetFoldersContent"
    icon = "folder-open"

    inputs = [
        DataInput(
            name="data",
            display_name="Folders and Files IDs",
            info="IDs of the folders and files to get",
            required=True,
        ),
        MessageTextInput(
            name="asc_auth_key",
            display_name="Auth key",
            info="Auth key to use",
            required=True,
        ),
        MessageInput(
            name="files_host",
            display_name="Files Service Host",
            info="Host URL for the files service",
            required=True,
        )
    ]

    outputs = [
        Output(
            name="folder_content",
            display_name="Folder Content",
            method="get_files_from_folders",
        ),
    ]

    async def get_folder(self, session: aiohttp.ClientSession, folder_id: str) -> Dict[str, Any]:
        """
        Make an async API request to get folder information from DocSpace.

        Args:
            session: aiohttp client session
            folder_id: ID of the folder to retrieve

        Returns:
            Dict containing the folder information including metadata and contents
        """
        try:
            headers = {
                'Authorization': self.asc_auth_key,
            }

            files_host = self.files_host.get_text()
            url = f'{files_host}/api/2.0/files/{folder_id}'

            async with session.get(url, headers=headers, timeout=30) as response:
                response.raise_for_status()
                data = await response.json()
                return data["response"]

        except Exception as e:
            print(f"Error getting folder {folder_id}: {str(e)}")
            return None

    async def fetch_all_folders(self, folder_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch all folders concurrently using aiohttp for efficient retrieval.

        Args:
            folder_ids: List of folder IDs to fetch from DocSpace

        Returns:
            List of folder information dictionaries with complete metadata
        """
        async with aiohttp.ClientSession() as session:
            # Create tasks for all file fetches
            tasks = [self.get_folder(session, folder_id)
                     for folder_id in folder_ids]
            # Wait for all tasks to complete (like Promise.all)
            results = await asyncio.gather(*tasks)
            # Filter out None results (failed requests)
            return [r for r in results if r is not None]

    async def get_files_from_folders(self) -> Data:
        """
        Make concurrent API requests to retrieve folders from DocSpace and extract their files.
        Processes the input folder IDs, fetches folder information, and extracts file metadata.

        Returns:
            Data object containing a list of file information dictionaries extracted from the folders
        """
        try:
            # Get folder IDs from input data
            folders_data: List[str] = self.data.data.get(
                "folders", [])

            if not folders_data:
                return Data(data={"content": []})

            # Fetch all folders concurrently
            folders_info = await self.fetch_all_folders(folders_data)

            content = []

            content.extend(folders_info[0].get('folders', []))
            content.extend(folders_info[0].get('files', []))

            return Data(data={"content": content})

        except Exception as e:
            return Data(data={"content": []})
