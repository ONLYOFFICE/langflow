from langflow.template import Output


class DataOutput(Output):
    display_name: str = "Data"
    name: str = "api_build_data"
    method: str = "build_data"


class ToolOutput(Output):
    display_name: str = "Tool"
    name: str = "api_build_tool"
    method: str = "build_tool"
    hidden: bool = True
