import requests
from langflow.custom import Component
from langflow.io import Output
from langflow.inputs.inputs import MessageTextInput, MessageInput
from langflow.schema import Message


class GetFilesCollectionNameComponent(Component):
    """Component for retrieving and formatting Qdrant collection name from DocSpace tenant ID."""


    display_name: str = "Qdrant Collection Name"
    description: str = "Retrieves tenant ID from DocSpace API and formats it as a Qdrant collection name for file storage"
    name: str = "GetFileCollectionName"
    icon = "database"

    inputs = [
        MessageTextInput(
            name="asc_auth_key",
            display_name="Auth key",
            info="Auth key to use",
            required=True,
        ),
        MessageInput(
            name="api_host",
            display_name="API Service",
            info="URL of the API service",
            required=True,
        )
    ]

    outputs = [
        Output(
            name="collection_name",
            display_name="Collection name",
            method="get_file_collection_name",
        ),

    ]

    def get_file_collection_name(self) -> Message:
        """
        Make an API request to get a file.

        Args:
            file_id: ID of the file to get

        Returns:
            Message object containing the response
        """
        try:
            headers = {}

            headers['Authorization'] = self.asc_auth_key

            api_host = self.api_host.text
            url = f'{api_host}/api/2.0/portal'

            response = requests.get(
                url,
                headers=headers,
                timeout=30  # 30 second timeout
            )

            # Raise an exception for bad status codes
            response.raise_for_status()

            msg = Message(
                text=f'files-{response.json()["response"]['tenantId']}')

            return msg

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error making API request: {str(e)}")
