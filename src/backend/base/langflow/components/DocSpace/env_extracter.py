import os
from langflow.custom import Component
from langflow.io import Output
from langflow.schema import Message


class EnvExtractorComponent(Component):
    """Component for extracting environment variables."""

    display_name: str = "Environment Variables Extractor"
    description: str = "Extract environment variables for DocSpace services"
    name: str = "EnvExtractor"
    icon = "settings"

    outputs = [
        Output(
            name="api_host",
            display_name="API Service",
            method="get_api_host",
        ),
        Output(
            name="files_host",
            display_name="Files Service",
            method="get_files_host",
        ),
        Output(
            name="qdrant_host",
            display_name="Qdrant Service",
            method="get_qdrant_host",
        ),
        Output(
            name="qdrant_port",
            display_name="Qdrant Port",
            method="get_qdrant_port",
        ),
    ]

    def get_api_host(self) -> Message:
        """
        Get the API service host from environment variables.

        Returns:
            Message object containing the API host URL
        """
        try:
            api_host = os.environ.get(
                'HOST_API_SERVICE', 'http://onlyoffice-api:5050')
            return Message(text=api_host)
        except Exception as e:
            raise ValueError(f"Error getting API host: {str(e)}")

    def get_files_host(self) -> Message:
        """
        Get the Files service host from environment variables.

        Returns:
            Message object containing the Files host URL
        """
        try:
            files_host = os.environ.get(
                'HOST_FILES_SERVICE', 'http://onlyoffice-files:5050')
            return Message(text=files_host)
        except Exception as e:
            raise ValueError(f"Error getting Files host: {str(e)}")

    def get_qdrant_host(self) -> Message:
        """
        Get the Qdrant service host from environment variables.

        Returns:
            Message object containing the Qdrant host URL
        """
        try:
            qdrant_host = os.environ.get(
                'HOST_QDRANT_SERVICE', 'onlyoffice-qdrant')
            return Message(text=qdrant_host)
        except Exception as e:
            raise ValueError(f"Error getting Qdrant host: {str(e)}")
            
    def get_qdrant_port(self) -> Message:
        """
        Get the Qdrant service port from environment variables.

        Returns:
            Message object containing the Qdrant port
        """
        try:
            qdrant_port = os.environ.get(
                'HOST_QDRANT_PORT', '6333')
            return Message(text=qdrant_port)
        except Exception as e:
            raise ValueError(f"Error getting Qdrant port: {str(e)}")
