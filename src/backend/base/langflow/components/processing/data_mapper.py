from langflow.template.field.base import Output
from langflow.schema.data import Data
from langflow.schema.message import Message
from langflow.custom import Component
from langflow.inputs.inputs import DataInput, DictInput
import json

class DataMapper(Component):
    display_name = "Data Mapper"
    description = (
        "Maps data using specified patterns to a new Data object or a JSON string. "
        "Patterns can be in the format 'object.field1.field2' or 'object.field1[0]'."
    )
    icon = "table"
    name = "DataMapper"    

    inputs = [
        DataInput(
            name="input_data",
            display_name="Data",
            info="Input data to map from.",
        ),
        DictInput(
            name="patterns",
            display_name="Patterns",
            info="Dictionary where keys are field names in the output and values are patterns to extract data (e.g., 'object.field1.field2' or 'object.field1[0]').",
            is_list=True,
        ),
    ]

    outputs = [
        Output(
            display_name="Data",
            name="data",
            method="build_data",
            info="A Data object built from the mapping process.",
        ),
        Output(
            display_name="Message",
            name="message",
            method="build_message",
            info="A message containing the mapped data as a JSON string.",
        ),
    ]

    def _get_value_from_path(self, data_dict, path):
        """Extract a value from a nested dictionary using a dot-notation path."""
        parts = path.split('.')
        current = data_dict
        
        for part in parts:
            # Check if this part contains array indexing
            if '[' in part and part.endswith(']'):
                # Split the part into field name and index
                field_name, index_part = part.split('[', 1)
                index = int(index_part[:-1])  # Remove the closing bracket and convert to int
                
                # Access the field and then the index
                if field_name in current and isinstance(current[field_name], list):
                    if 0 <= index < len(current[field_name]):
                        current = current[field_name][index]
                    else:
                        # Index out of range
                        return None
                else:
                    # Field doesn't exist or is not a list
                    return None
            else:
                # Regular field access
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    # Field doesn't exist
                    return None
                    
        return current

    def _map_data(self):
        """Maps data using specified patterns and returns a dictionary."""
        input_data = self.input_data
        patterns = self.patterns
        
        # Initialize result dictionary
        result_data = {}
        
        # Get the source data dictionary
        if isinstance(input_data, Data):
            source_data = input_data.data
        elif isinstance(input_data, dict):
            source_data = input_data
        else:
            # If input is neither Data nor dict, return empty dictionary
            return {}
        
        # Process each pattern in the dictionary
        for field_name, pattern in patterns.items():
            # Extract the value using the path
            value = self._get_value_from_path(source_data, pattern)
            
            # If field_name is empty or None, use the last part of the pattern as field name
            if not field_name:
                if '[' in pattern and pattern.split('.')[-1].endswith(']'):
                    # Handle array indexing in the last part
                    last_part = pattern.split('.')[-1]
                    field_name = last_part.split('[')[0]
                else:
                    field_name = pattern.split('.')[-1]
            
            # Add to result if value was found
            if value is not None:
                result_data[field_name] = value
        
        return result_data

    def build_data(self) -> Data:
        """Maps data using specified patterns to a new Data object."""
        result_data = self._map_data()
        # Create and return a new Data object
        return Data(data=result_data)
    
    def build_message(self) -> Message:
        """Maps data using specified patterns and returns a JSON string message."""
        result_data = self._map_data()
        # Convert the result to a JSON string
        try:
            json_string = json.dumps(result_data, indent=2, default=str)
            return Message(text=json_string)
        except Exception as e:
            return Message(text=f"Error converting to JSON: {str(e)}", error=True)