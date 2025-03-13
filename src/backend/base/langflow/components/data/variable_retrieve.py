from langflow.custom import Component
from langflow.inputs.inputs import HandleInput, MessageTextInput
from langflow.schema.data import Data
from langflow.template.field.base import Output


class VariableRetrieveComponent(Component):
    display_name = "Variable Retrieve"
    description = "A component to retrieve a variable from the graph state."
    icon = "Database"
    name = "VariableRetrieve"

    inputs = [
        MessageTextInput(
            name="variable_name",
            display_name="Variable Name",
            info="The name of the variable to retrieve.",
            required=True,
        ),
        HandleInput(
            name="ignored_input",
            display_name="Input",
            info="An input to trigger the component execution (value is ignored).",
            input_types=["Data", "DataFrame", "Message"],
            required=False,
        ),
    ]

    outputs = [
        Output(name="output_value", display_name="Value", method="retrieve_variable")
    ]

    def retrieve_variable(self) -> Data:
        try:
            variable_name = getattr(self, "variable_name", None)
            if not variable_name:
                self.status = "Error: 'Variable Name' is required."
                error_message = "The 'Variable Name' input cannot be empty"
                raise ValueError(error_message)

            value = self.get_state(variable_name)
            
            if value is None:
                self.status = f"Variable '{variable_name}' not found in graph state"
                return Data(data={"text": ""})

            if not isinstance(value, Data):
                value = Data(data={"text": str(value)})

            self.status = f"Variable '{variable_name}' retrieved successfully"
            return value
        except Exception as exc:
            error_msg = f"Error retrieving variable: {exc!s}"
            self.status = error_msg
            raise
