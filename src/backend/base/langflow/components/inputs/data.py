from langflow.custom import Component
from langflow.io import DataInput, Output
from langflow.schema.data import Data


class DataInputComponent(Component):
    display_name = "Data Input"
    description = "Get data and pass it to the next iteration."
    icon = "Database"
    name = "DataInput"

    inputs = [
        DataInput(
            name="input_data",
            display_name="Data",
            info="Data to be passed as input.",
        ),
    ]
    outputs = [
        Output(display_name="Data", name="data", method="process_data"),
    ]

    def process_data(self) -> Data:
        """Simply pass the data to the next component."""
        # If it's already a Data object, return it
        if isinstance(self.input_data, Data):
            return self.input_data

        # If it's a dict, convert to Data
        if isinstance(self.input_data, dict):
            return Data(**self.input_data)

        # For anything else, create a Data object with a text field
        return Data(text=str(self.input_data))
