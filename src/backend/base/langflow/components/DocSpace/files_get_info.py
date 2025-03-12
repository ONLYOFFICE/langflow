import asyncio
import aiohttp
from typing import List, Dict, Any
from langflow.custom import Component
from langflow.inputs.inputs import MessageInput, MessageTextInput
from langflow.io import Output
from langflow.schema import Data, Message


class GetFilesInfoComponent(Component):
    """Component for retrieving file information from DocSpace via API."""


    display_name: str = "Get File Info"
    description: str = "Retrieves detailed file information from DocSpace including metadata, permissions, and file properties"
    name: str = "GetFile"
    icon = "file-info"

    inputs = [
        MessageInput(
            name="files_ids",
            display_name="Files IDs",
            info="IDs of the files to get",
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
            display_name="Files Service",
            info="URL of the files service",
            required=True,
        )
    ]

    outputs = [
        Output(
            name="files",
            display_name="Files",
            method="get_files",
        ),
    ]

    async def get_file(self, session: aiohttp.ClientSession, file_id: str) -> Dict[str, Any]:
        """
        Make an async API request to get a file.

        Args:
            session: aiohttp client session
            file_id: ID of the file to get

        Returns:
            Dict containing the file information
        """
        try:
            headers = {
                'Authorization': self.asc_auth_key,
            }

            files_host = self.files_host.text
            url = f'{files_host}/api/2.0/files/file/{file_id}'

            async with session.get(url, headers=headers, timeout=30) as response:
                response.raise_for_status()
                data = await response.json()
                return data["response"]

        except Exception as e:
            print(f"Error getting file {file_id}: {str(e)}")
            return None

    async def fetch_all_files(self, file_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch all files concurrently using aiohttp.

        Args:
            file_ids: List of file IDs to fetch

        Returns:
            List of file information dictionaries
        """
        async with aiohttp.ClientSession() as session:
            # Create tasks for all file fetches
            tasks = [self.get_file(session, file_id) for file_id in file_ids]
            # Wait for all tasks to complete (like Promise.all)
            results = await asyncio.gather(*tasks)
            # Filter out None results (failed requests)
            return [r for r in results if r is not None]

    async def get_files(self) -> Data:
        """
        Make concurrent API requests to get multiple files.

        Returns:
            Data object containing list of file information
        """
        try:
            # Get file IDs from input data
            files_data: List[str] = self.files_ids.data.get("files_ids", [])
            if not files_data:
                return Data(data={"files": []})

            # Fetch all files concurrently
            files_info = await self.fetch_all_files(files_data)
            return Data(data={"files": files_info})

        except Exception as e:
            return Data(data={"files": []})
