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

        Returns:
            Data object with extracted references and text
        """
        try:
            # Get text from input Message object
            input_message: Message = self.input

            text = input_message.get_text()
            if not isinstance(text, str) or not text:
                return Data(data={})

            # Split input into references and text parts
            parts = text.split(' ', 1)
            ref_part = parts[0]  # First part with @references
            text_part = parts[1] if len(parts) > 1 else ''  # Rest is the text

            # Extract references from the first part
            references = []
            if ref_part.startswith('@'):
                # Split by comma and clean up @ symbols
                refs = ref_part.split(',')
                references = [ref.strip().lstrip('@') for ref in refs]

            result = {
                "references": references,
                "text": text_part
            }

            return Data(data=result)

        except Exception as e:
            raise Exception(f"Error parsing input: {str(e)}")
