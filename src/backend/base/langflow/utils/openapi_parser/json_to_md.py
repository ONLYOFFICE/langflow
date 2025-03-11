from typing import Dict, Any, List

from .types import EndpointInfo


def create_table_row(columns: List[str]) -> str:
    """Create a markdown table row."""
    return f"| {' | '.join(columns)} |"


def format_value(value: Any) -> str:
    """Format a value for markdown display."""
    if isinstance(value, bool):
        return f"`{str(value).lower()}`"
    elif isinstance(value, (int, float)):
        return f"`{value}`"
    elif isinstance(value, str):
        formatted_value = f"`\"{value}\"`"
        return formatted_value
    elif isinstance(value, list):
        return f"`{value}`"
    elif value is None:
        return "—"
    return str(value)


def format_constraints(prop: Dict[str, Any]) -> str:
    """Format property constraints for markdown."""
    constraints = []

    if isinstance(prop, dict):
        # Handle required field
        if prop.get("required", False):
            constraints.append("required")

        # Handle length constraints
        if "minLength" in prop:
            constraints.append(f"`minLength: {prop['minLength']}`")
        if "maxLength" in prop:
            constraints.append(f"`maxLength: {prop['maxLength']}`")

        # Handle format
        if "format" in prop:
            constraints.append(f"`{prop['format']}`")

        # Handle nullable
        if prop.get("nullable", False):
            constraints.append("nullable")

        # Handle minimum/maximum
        if "minimum" in prop:
            constraints.append(f"`minimum: {prop['minimum']}`")
        if "maximum" in prop:
            constraints.append(f"`maximum: {prop['maximum']}`")

        # Handle pattern
        if "pattern" in prop:
            constraints.append(f"`pattern: {prop['pattern']}`")

        # Handle enums
        if "enum" in prop:
            enum_values = prop['enum']
            if enum_values:
                if isinstance(enum_values[0], str):
                    constraints.append(
                        "enum: " + ", ".join(f"`{val}`" for val in enum_values))
                else:
                    constraints.append("enum: " + ", ".join(str(val)
                                       for val in enum_values))

        # Handle arrays
        if "type" in prop and prop["type"] == "array":
            if "items" in prop:
                items = prop["items"]
                if isinstance(items, dict):
                    item_type = items.get("type", "any")
                    if "$ref" in items:
                        item_type = items["$ref"].split("/")[-1]
                else:
                    item_type = str(items)
                constraints.append(f"array of {item_type}")

        # Handle oneOf
        if "oneOf" in prop:
            one_of_types = []
            for variant in prop["oneOf"]:
                if "type" in variant:
                    one_of_types.append(f"`{variant['type']}`")
                if "enum" in variant:
                    one_of_types.append("enum")
            if one_of_types:
                constraints.append(f"one of: {', '.join(one_of_types)}")

    return ", ".join(constraints) if constraints else "—"


def format_property_table(properties: Dict[str, Any], components: Dict[str, Any] = None) -> str:
    """Format properties into a markdown table."""
    headers = ["Property", "Type", "Description", "Constraints", "Example"]
    table = [
        create_table_row(headers),
        create_table_row(["---"] * len(headers))
    ]

    for prop_name, prop in sorted(properties.items()):
        # Handle string references directly
        if isinstance(prop, str):
            prop_type = prop
            prop = {"type": prop}
        elif isinstance(prop, dict):
            # Get property type
            prop_type = prop.get('type', 'any')

            # Handle special types
            if "$ref" in prop:
                prop_type = prop["$ref"].split("/")[-1]
            elif prop_type == "object" and "properties" in prop:
                prop_type = prop.get('title', 'object')
            elif prop_type == "array" and "items" in prop:
                items = prop["items"]
                if isinstance(items, dict):
                    item_type = items.get("type", "any")
                    if "$ref" in items:
                        item_type = items["$ref"].split("/")[-1]
                else:
                    item_type = str(items)
                prop_type = f"{item_type}[]"

        # Get component description if available
        description = prop.get('description', '—')
        if components and prop_type in components:
            component = components[prop_type]
            if "description" in component:
                description = component["description"]

        # Format the row
        row = [
            f"**{prop_name}**",
            f"`{prop_type}`",
            description,
            format_constraints(prop),
            format_value(prop.get('example'))
        ]
        table.append(create_table_row(row))

    return "\n".join(table)


def format_component(name: str, schema: Dict[str, Any], components: Dict[str, Any] = None) -> str:
    """Format a component schema into markdown."""
    sections = [f"#### **{name}**"]

    if "description" in schema:
        sections.append(f"> {schema['description']}\n")

    if "oneOf" in schema:
        sections.append("One of the following:")
        for variant in schema["oneOf"]:
            sections.append("\n**Option:**")
            if "description" in variant:
                sections.append(f"- Description: {variant['description']}")
            if "enum" in variant:
                if isinstance(variant['enum'][0], str):
                    values = ", ".join(f"`{val}`" for val in variant['enum'])
                else:
                    values = ", ".join(str(val) for val in variant['enum'])
                sections.append(f"- Values: {values}")
            if "type" in variant:
                sections.append(f"- Type: `{variant['type']}`")
            if "example" in variant:
                sections.append(f"- Example: `{variant['example']}`")
    elif "properties" in schema:
        sections.append(format_property_table(
            schema["properties"], components))
    elif "enum" in schema:
        sections.append("**Enum Values:**")
        enum_values = schema["enum"]
        if isinstance(enum_values[0], str):
            values = ", ".join(f"`{val}`" for val in enum_values)
        else:
            values = ", ".join(str(val) for val in enum_values)
        sections.append(f"- Values: {values}")
        if "description" in schema:
            sections.append(f"- Description: {schema['description']}")
        if "example" in schema:
            sections.append(f"- Example: `{schema['example']}`")

    return "\n".join(sections)


def endpoint_to_md(endpoint: EndpointInfo) -> str:
    """Convert endpoint information to markdown documentation."""
    sections = []

    # Method and path
    method = endpoint.get("method", "").upper()
    path = endpoint.get("path", "")
    sections.append(f"# {method} {path}\n")

    # Summary/Description
    if "summary" in endpoint:
        sections.append(endpoint["summary"])

    # Request section - only add if there are parameters or request body
    has_request_content = False
    request_sections = []

    # Query Parameters
    if "parameters" in endpoint:
        query_params = [p for p in endpoint["parameters"]
                        if p.get("in") == "query"]
        if query_params:
            has_request_content = True
            sections.append("### **Query Parameters**\n")
            headers = ["Parameter", "Type",
                       "Description", "Required", "Example"]
            table = [
                create_table_row(headers),
                create_table_row(["---"] * len(headers))
            ]

            for param in sorted(query_params, key=lambda x: (not x.get("required", False), x.get("name", ""))):
                schema = param.get('schema', {})
                param_type = schema.get('type', 'any')
                if param_type == 'array' and 'items' in schema:
                    items = schema['items']
                    if isinstance(items, dict):
                        item_type = items.get('type', 'any')
                        if '$ref' in items:
                            item_type = items['$ref'].split('/')[-1]
                    else:
                        item_type = str(items)
                    param_type = f"{item_type}[]"
                elif '$ref' in schema:
                    param_type = schema['$ref'].split('/')[-1]

                constraints = []
                if param.get('required', False):
                    constraints.append('required')
                if schema.get('nullable', False):
                    constraints.append('nullable')
                if 'enum' in schema:
                    enum_values = schema['enum']
                    if enum_values:
                        constraints.append(
                            'enum: ' + ', '.join(f'`{val}`' for val in enum_values))

                row = [
                    f"**{param.get('name', '')}**",
                    f"`{param_type}`",
                    param.get('description', '—'),
                    ', '.join(constraints) if constraints else '—',
                    format_value(param.get('example', schema.get('example')))
                ]
                table.append(create_table_row(row))
            request_sections.append("\n".join(table) + "\n")

    # Request Body
    if "requestBody" in endpoint:
        has_request_content = True
        request_sections.append("### **Request Body**\n")
        request_body = endpoint["requestBody"]
        if "content" in request_body:
            content = request_body["content"]
            if isinstance(content, dict):
                for content_type, content_schema in content.items():
                    request_sections.append(
                        f"Content Type: `{content_type}`\n")
                    if "schema" in content_schema:
                        schema = content_schema["schema"]
                        if "$ref" in schema and "components" in endpoint:
                            ref_name = schema["$ref"].split("/")[-1]
                            if ref_name in endpoint["components"]:
                                component = endpoint["components"][ref_name]
                                request_sections.append(format_component(
                                    ref_name, component, endpoint["components"]))
                        else:
                            request_sections.append(format_component(
                                "schema", schema, endpoint.get("components")))
            elif isinstance(content, str):
                request_sections.append(f"Content Type: `{content}`\n")
                if content in endpoint.get("components", {}):
                    component = endpoint["components"][content]
                    request_sections.append(format_component(
                        content, component, endpoint["components"]))

    # Responses
    if "responses" in endpoint:
        # Only add horizontal rule if we had content before
        if has_request_content or "summary" in endpoint:
            sections.append("\n---\n")
        sections.append("## **Responses**\n")
        for status_code, response in sorted(endpoint["responses"].items()):
            sections.append(f"### **{status_code}**")
            sections.append(
                f"- **Description**: {response.get('description', '—')}")
            if "content" in response:
                content = response["content"]
                if isinstance(content, dict):
                    for content_type, content_schema in content.items():
                        sections.append(f"- **Schema**: `{content_type}`")
                        if "schema" in content_schema:
                            schema = content_schema["schema"]
                            if "$ref" in schema and "components" in endpoint:
                                ref_name = schema["$ref"].split("/")[-1]
                                if ref_name in endpoint["components"]:
                                    component = endpoint["components"][ref_name]
                                    sections.append(
                                        "\n" + format_component(ref_name, component, endpoint["components"]))
                            else:
                                sections.append(
                                    "\n" + format_component("schema", schema, endpoint.get("components")))
                elif isinstance(content, str):
                    sections.append(f"- **Schema**: `{content}`")
                    if content in endpoint.get("components", {}):
                        component = endpoint["components"][content]
                        sections.append(
                            "\n" + format_component(content, component, endpoint["components"]))
                sections.append("\n")

    # Add Request section only if it has content
    if has_request_content:
        sections.append("## **Request**\n")
        sections.extend(request_sections)

    # Components/Sub-components
    if "components" in endpoint:
        # Track if we've added any components
        has_sub_components = False
        sub_component_sections = []

        for comp_name, comp_schema in sorted(endpoint["components"].items()):
            # Skip components that are already documented elsewhere
            skip_components = set()
            if "requestBody" in endpoint and "content" in endpoint["requestBody"]:
                content = endpoint["requestBody"]["content"]
                if isinstance(content, dict):
                    for content_schema in content.values():
                        if "schema" in content_schema and "$ref" in content_schema["schema"]:
                            skip_components.add(
                                content_schema["schema"]["$ref"].split("/")[-1])
                elif isinstance(content, str):
                    skip_components.add(content)

            for resp in endpoint.get("responses", {}).values():
                if "content" in resp:
                    content = resp["content"]
                    if isinstance(content, dict):
                        for content_schema in content.values():
                            if "schema" in content_schema and "$ref" in content_schema["schema"]:
                                skip_components.add(
                                    content_schema["schema"]["$ref"].split("/")[-1])
                    elif isinstance(content, str):
                        # If content is a string, it's likely a direct reference
                        skip_components.add(content)

            if comp_name not in skip_components:
                has_sub_components = True
                sub_component_sections.append(format_component(
                    comp_name, comp_schema, endpoint["components"]) + "\n")

        # Only add sub-components section if we have components to show
        if has_sub_components:
            # Only add horizontal rule if we had content before
            if len(sections) > 1:  # More than just the title
                sections.append("\n---\n")
            sections.append("### **Sub-components**\n")
            sections.extend(sub_component_sections)

    return "\n".join(sections)
