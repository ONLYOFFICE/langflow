from langflow.template.field.base import Output
from langflow.schema.data import Data
from langflow.schema.message import Message
from langflow.custom import Component
from langflow.inputs.inputs import DataInput, DictInput
import json

class DataMapper(Component):
    display_name = "Data Mapper"
    description = "Maps data using patterns or literal values to a new Data object or JSON string."
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
            info="Dictionary where keys are field names in the output and values are either patterns in curly brackets {object.field1.field2} or {object.array[0]} or literal values.",
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
        parts = path.split('.')
        current = data_dict
        
        for part in parts:
            if '[' in part and part.endswith(']'):
                field_name, index_part = part.split('[', 1)
                index = int(index_part[:-1])
                
                if field_name in current and isinstance(current[field_name], list):
                    if 0 <= index < len(current[field_name]):
                        current = current[field_name][index]
                    else:
                        return None
                else:
                    return None
            else:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
                    
        return current

    def _map_data(self):
        input_data = self.input_data
        patterns = self.patterns
        
        result_data = {}
        
        if isinstance(input_data, Data):
            source_data = input_data.data
        elif isinstance(input_data, dict):
            source_data = input_data
        else:
            return {}
        
        for field_name, value in patterns.items():
            if isinstance(value, str) and value.startswith('{') and value.endswith('}'): 
                pattern = value[1:-1]
                extracted_value = self._get_value_from_path(source_data, pattern)
                
                if not field_name:
                    if '[' in pattern and pattern.split('.')[-1].endswith(']'):
                        last_part = pattern.split('.')[-1]
                        field_name = last_part.split('[')[0]
                    else:
                        field_name = pattern.split('.')[-1]
                
                if extracted_value is not None:
                    result_data[field_name] = extracted_value
            else:
                result_data[field_name] = value
        
        return result_data

    def build_data(self) -> Data:
        result_data = self._map_data()
        return Data(data=result_data)
    
    def build_message(self) -> Message:
        result_data = self._map_data()
        try:
            json_string = json.dumps(result_data, indent=2, default=str)
            return Message(text=json_string)
        except Exception as e:
            return Message(text=f"Error converting to JSON: {str(e)}", error=True)