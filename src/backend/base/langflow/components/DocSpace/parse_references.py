from typing import List, Dict, Any, Union
from langflow.custom import Component
from langflow.inputs.inputs import DataInput
from langflow.io import Output
from langflow.schema import Data, Message


class ReferencesParserComponent(Component):
    display_name: str = "Parse References"
    description: str = "Parse references from input data to extract files, folders, and flags."
    name: str = "ParseReferences"
    icon = "braces"

    inputs = [
        DataInput(
            name="input",
            display_name="Data",
            info="Input data containing references",
            required=True,
        ),
    ]

    outputs = [
        Output(display_name="Parsed references",
               name="parsed_references", method="parse_references"),
    ]

    def parse_references(self) -> Data:
        """Parse input data to extract and categorize references.

        Sorts input array into:
        - files: numeric IDs as integers
        - folders: folder numbers extracted from 'folder-X' format
        - docspace_api: True if 'docspace-api' is in the input
        - docspace_sdk: True if 'docspace-sdk' is in the input

        Returns:
            Data: Parsed references with files, folders, and flags
        """
        input_data = self.input.data

        if not input_data:
            return Data(data={
                "files": [],
                "folders": [],
                "docspace_api": False,
                "docspace_sdk": False
            })

        # Extract references from input
        references = input_data.get("references", [])

        # Initialize result containers
        files = []
        folders = []
        docspace_api = False
        docspace_sdk = False

        # Process each reference
        for ref in references:
            # Convert to string to handle different types
            ref_str = str(ref).strip()

            # Check if it's a file ID (numeric)
            if ref_str.isdigit():
                files.append(int(ref_str))
            # Check if it's a folder reference
            elif ref_str.startswith("folder-"):
                try:
                    folder_id = int(ref_str.replace("folder-", ""))
                    folders.append(folder_id)
                except ValueError:
                    # Skip invalid folder format
                    pass
            # Check for docspace API/SDK flags
            elif ref_str == "docspace-api":
                docspace_api = True
            elif ref_str == "docspace-sdk":
                docspace_sdk = True

        # Return structured data
        return Data(data={
            "files": files,
            "folders": folders,
            "docspace_api": docspace_api,
            "docspace_sdk": docspace_sdk
        })
