from langflow.custom import Component
from langflow.inputs.inputs import DataInput, MessageTextInput
from langflow.schema.data import Data
from langflow.template.field.base import Output


class VariableStoreComponent(Component):
    display_name = "Variable Store"
    description = "A component to store a variable in the graph state."
    icon = "Database"
    name = "VariableStore"

    inputs = [
        MessageTextInput(
            name="variable_name",
            display_name="Variable Name",
            info="The name of the variable to store.",
            required=True,
        ),
        DataInput(
            name="value",
            display_name="Value",
            info="The value of the variable to store.",
        ),
    ]

    outputs = [
        Output(name="output_value", display_name="Value", method="store_variable")
    ]

    def store_variable(self) -> Data:
        try:
            variable_name = getattr(self, "variable_name", None)
            if not variable_name:
                self.status = "Error: 'Variable Name' is required."
                error_message = "The 'Variable Name' input cannot be empty"
                raise ValueError(error_message)

            value = getattr(self, "value", None)
            if value is None:
                value = Data(data={"text": ""})
            elif not isinstance(value, Data):
                value = Data(data={"text": str(value)})
                
            self.update_state(variable_name, value)

            self.status = f"Variable '{variable_name}' stored successfully"
            return value
        except Exception as exc:
            error_msg = f"Error storing variable: {exc!s}"
            self.status = error_msg
            raise
