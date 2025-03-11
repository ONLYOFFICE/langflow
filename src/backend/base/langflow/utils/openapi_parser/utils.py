"""
Utility Functions for OpenAPI Schema Analysis

This module provides helper functions for analyzing OpenAPI schemas and their
relationships. It focuses on extracting and tracking component references and
dependencies within schema definitions.

The functions in this module are designed to work with OpenAPI 3.0.1 specification
and handle various ways that components can reference each other, including:
- Direct references ($ref)
- Property definitions
- Array items
- Inheritance (allOf, oneOf, anyOf)
"""

from typing import Dict, Set


from .types import EndpointInfo, OpenAPIDocument, TagObject, SchemaObject


def extract_component_refs(schema: Dict) -> Set[str]:
    """
    Recursively extract component references from a schema.

    This function analyzes an OpenAPI schema and finds all components that it
    references, either directly or through nested structures. It handles:
    - Direct references using $ref
    - Properties of objects
    - Items in arrays
    - Inheritance using allOf, oneOf, anyOf

    Args:
        schema (Dict): Schema to extract references from. This can be any valid
                      OpenAPI schema object, including:
                      - A component schema
                      - A property definition
                      - A parameter schema
                      - A request/response body schema

    Returns:
        Set[str]: Set of component names referenced in the schema. For example,
                 if a User schema references Address and PhoneNumber components,
                 this would return {"Address", "PhoneNumber"}.

    Example:
        >>> schema = {
        ...     "type": "object",
        ...     "properties": {
        ...         "address": {"$ref": "#/components/schemas/Address"},
        ...         "phones": {
        ...             "type": "array",
        ...             "items": {"$ref": "#/components/schemas/PhoneNumber"}
        ...         }
        ...     }
        ... }
        >>> extract_component_refs(schema)
    """
    refs = set()

    # Check for direct reference
    if "$ref" in schema:
        ref = schema["$ref"]
        if ref.startswith("#/components/schemas/"):
            refs.add(ref.split("/")[-1])
        return refs

    # Check nested properties
    if "properties" in schema:
        for prop in schema["properties"].values():
            refs.update(extract_component_refs(prop))

    # Check items in arrays
    if "items" in schema:
        refs.update(extract_component_refs(schema["items"]))

    # Check anyOf, oneOf, allOf
    for key in ["anyOf", "oneOf", "allOf"]:
        if key in schema:
            for item in schema[key]:
                refs.update(extract_component_refs(item))

    return refs


def extract_endpoints(content: OpenAPIDocument) -> Dict[str, EndpointInfo]:
    """
    Extract endpoint information from OpenAPI content.

    Args:
        content (OpenAPIDocument): Dictionary of YAML files and their contents

    Returns:
        Dict[str, EndpointInfo]: Dictionary mapping endpoint paths to their details
    """
    endpoints = {}

    version = content.get("info", {}).get("version", "")
    for path, path_data in content.get("paths", {}).items():
        for method, method_data in path_data.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                tags = []
                for tag in method_data.get("tags", []):
                    # First normalize spaces and slashes
                    tag_name = tag.strip()
                    # Remove all spaces
                    tag_name = tag_name.replace(" ", "").replace("/", "")
                    if tag_name:
                        tags.append(tag_name)

                endpoint_key = f"{path}_{method}"
                endpoints[endpoint_key] = {
                    "path": path,
                    "method": method,
                    "summary": method_data.get("summary", ""),
                    "version": version,
                    "tags": tags,
                    "operationId": method_data.get("operationId", ""),
                    "responses": method_data.get("responses", {}),
                    "parameters": method_data.get("parameters", []),
                    "requestBody": method_data.get("requestBody", {})

                }

    return endpoints


def extract_tags(content: OpenAPIDocument) -> Dict[str, TagObject]:
    """
    Extract all tags from OpenAPI YAML content.

    Args:
        contents_to_process (OpenAPIDocument): Dictionary of YAML files and their contents

    Returns:
        Dict[str, TagObject]: Dictionary mapping tag names to their details
    """
    tags = {}

    for tag in content.get("tags", []):
        # First normalize spaces and slashes
        tag_name = tag.get("name", "").strip()
        # Remove all spaces
        tag_name = tag_name.replace(" ", "").replace("/", "")
        if tag_name:
            tag_info = {
                "name": tag_name,
                "description": tag.get("description", ""),
                "version": content.get("info", {}).get("version", "").strip()
            }
            tags[tag_name] = tag_info

    return tags


def extract_components(content: OpenAPIDocument) -> Dict[str, SchemaObject]:
    """
    Extract all component schemas from OpenAPI YAML content.

    Args:
        content (OpenAPIDocument): Dictionary of YAML files and their contents

    Returns:
        Dict[str, SchemaObject]: Dictionary mapping component names to their schemas
    """
    result_components = {}

    version = content.get("info", {}).get("version", "")

    components = content.get("components", {})
    schemas = components.get("schemas", {})

    for component_name, schema in schemas.items():
        schema["version"] = version

        result_components[component_name] = schema

    return result_components
