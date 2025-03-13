import re


from langflow.custom import Component
from langflow.inputs.inputs import MessageInput
from langflow.io import Output
from langflow.schema import Data, Message


class InputParserComponent(Component):
    display_name: str = "Parse input"
    description: str = "Parse an input and return a parsed data object."
    name: str = "InputParser"
    icon = "braces"

    inputs = [
        MessageInput(
            name="input",
            display_name="Input",
            info="User input to parse",
            required=True,
        ),
    ]

    outputs = [
        Output(display_name="Parsed data",
               name="parsed_data", method="parse_input"),
    ]

    def parse_input(self) -> Data:
        """Parse input text to extract references.

        References can be in the following formats:
        - @123 (file ID)
        - @folder-123 (folder ID)
        - References can appear anywhere in the text

        Returns:
            Data object with extracted references and text
        """
        try:
            # Get text from input Message object
            input_message: Message = self.input

            text = input_message.get_text()
            if not isinstance(text, str) or not text:
                return Data(data={})

            # Define regex patterns for file and folder references
            file_pattern = r'@(\d+)'  # Matches @123 (file ID)
            folder_pattern = r'@folder-(\d+)'  # Matches @folder-123 (folder ID)
            
            # Extract all references
            file_refs = re.findall(file_pattern, text)
            folder_refs = re.findall(folder_pattern, text)
            
            # Combine all references
            references = file_refs + [f"folder-{ref}" for ref in folder_refs]
            
            # Remove references from text if they are at the beginning
            # This maintains backward compatibility with the old format
            cleaned_text = text
            parts = text.split(' ', 1)
            if parts[0].startswith('@'):
                cleaned_text = parts[1] if len(parts) > 1 else ''
            
            result = {
                "references": references,
                "text": cleaned_text,
                "original_text": text
            }

            return Data(data=result)

        except Exception as e:
            raise Exception(f"Error parsing input: {str(e)}")
