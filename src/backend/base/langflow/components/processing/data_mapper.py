from langflow.template.field.base import Output
from langflow.schema.data import Data
from langflow.schema.message import Message
from langflow.custom import Component
from langflow.inputs.inputs import DataInput, DictInput, IntInput
from langflow.schema.dotdict import dotdict
from langflow.field_typing.range_spec import RangeSpec
from typing import Any
import json


class DataMapper(Component):
    display_name = "Data Mapper"
    description = "Maps data using patterns or literal values to a new Data object or JSON string."
    icon = "table"
    name = "DataMapper"
    MAX_FIELDS = 15

    inputs = [
        DataInput(
            name="input_data",
            display_name="Data",
            info="Input data to map from.",
        ),
        IntInput(
            name="number_of_fields",
            display_name="Number of Fields",
            info="Number of field mappings to define.",
            real_time_refresh=True,
            value=1,
            range_spec=RangeSpec(min=1, max=MAX_FIELDS, step=1, step_type="int"),
        ),
    ]

    outputs = [
        Output(
            display_name="Data",
            name="data",
            method="build_data"
        ),
        Output(
            display_name="Message",
            name="message",
            method="build_message",
        ),
    ]

    def update_build_config(self, build_config: dotdict, field_value: Any, field_name: str | None = None):
        if field_name == "number_of_fields":
            try:
                field_value_int = int(field_value)
            except ValueError:
                return build_config

            if field_value_int > self.MAX_FIELDS:
                build_config["number_of_fields"]["value"] = self.MAX_FIELDS
                msg = f"Number of fields cannot exceed {self.MAX_FIELDS}."
                raise ValueError(msg)

            existing_fields = {}

            for i in range(1, field_value_int + 1):
                field_field = f"field_{i}"

                if field_field in existing_fields:
                    build_config[field_field] = existing_fields[field_field]
                else:
                    field = DictInput(
                        display_name=f"Field {i}",
                        name=field_field,
                        info=f"Key-value pair where key is the output field name and value is either a pattern in curly brackets {{{{object.field}}}} or a literal value.",
                        input_types=["Message"],
                    )
                    build_config[field.name] = field.to_dict()

            build_config["number_of_fields"]["value"] = field_value_int
        return build_config

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
        fields = self._get_fields()

        result_data = {}

        if isinstance(input_data, Data):
            source_data = input_data.data
        elif isinstance(input_data, dict):
            source_data = input_data
        else:
            return {}

        for field_name, value in fields.items():
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

    def _get_fields(self):
        fields = {}

        num_fields = getattr(self, "number_of_fields", 0)

        for i in range(1, num_fields + 1):
            field_field = f"field_{i}"

            if hasattr(self, field_field):
                field_input = getattr(self, field_field, {})

                if isinstance(field_input, dict) and field_input:
                    for key, value in field_input.items():
                        if isinstance(value, Message):
                            fields[key] = value.text
                        else:
                            fields[key] = value
                elif isinstance(field_input, Message):
                    fields[field_input.text] = field_input.text

        return fields

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