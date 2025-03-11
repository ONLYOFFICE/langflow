"""
Parser module for handling OpenAPI endpoints.

This module provides functionality to extract and analyze endpoint information
from OpenAPI specifications.
"""

import copy

from typing import Dict, List, Set, Any


from .types import EndpointInfo, OpenAPIDocument


from .utils import extract_endpoints


class EndpointsParser:
    """Parser for extracting and analyzing endpoint information from OpenAPI specs."""

    @staticmethod
    def get_all_endpoint_names(content: OpenAPIDocument) -> List[str]:
        """
        Get a list of all available endpoint names.

        Returns:
            List[str]: List of endpoint names
        """
        endpoints = extract_endpoints(content)

        return list(endpoints.keys())

    @staticmethod
    def get_all_endpoints_info(content: OpenAPIDocument) -> Dict[str, EndpointInfo]:
        """
        Get detailed information about all endpoints.

        Returns:
            Dict[str, EndpointInfo]: Dictionary mapping endpoint names to their
                information
        """
        endpoints = {}

        for endpoint_name, endpoint in extract_endpoints(content).items():
            endpoints[endpoint_name] = EndpointsParser.normalize_endpoint_content(
                endpoint)

            dependencies = EndpointsParser.get_endpoint_components(endpoint)

            endpoints[endpoint_name]["dependencies"] = dependencies

        return endpoints

    @staticmethod
    def get_endpoint_components(endpoint: EndpointInfo) -> Set[str]:
        """
        Get all component references used in an endpoint, including nested components.

        Args:
            endpoint: The endpoint information to analyze

        Returns:
            Set[str]: Set of component names referenced in the endpoint
        """
        components = set()

        def extract_refs(obj: Any) -> None:
            if not isinstance(obj, dict):
                return

            # Check for $ref key
            if '$ref' in obj:
                ref = obj['$ref']
                if ref.startswith('#/components/schemas/'):
                    component_name = ref.split('/')[-1]
                    components.add(component_name)

            # Recursively check all dictionary values
            for value in obj.values():
                if isinstance(value, dict):
                    extract_refs(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            extract_refs(item)

        # Check request body
        if 'requestBody' in endpoint:
            extract_refs(endpoint['requestBody'])

        # Check parameters
        if 'parameters' in endpoint:
            for param in endpoint['parameters']:
                extract_refs(param)

        # Check responses
        if 'responses' in endpoint:
            extract_refs(endpoint['responses'])

        return components

    @staticmethod
    def normalize_endpoint_content(endpoint: EndpointInfo) -> EndpointInfo:
        """
        Normalize both request body and responses content by removing duplicate references
        and keeping only application/json format.

        Args:
            endpoint: Endpoint to normalize
        """

        cloned_endpoint = copy.deepcopy(endpoint)

        normalized_endpoint = EndpointsParser.normalize_response_content(
            EndpointsParser.normalize_request_body(cloned_endpoint)
        )

        return normalized_endpoint

    @staticmethod
    def normalize_response_content(endpoint: EndpointInfo) -> EndpointInfo:
        """
        Normalize response content by simplifying schema references.
        For example, if response has a schema reference like:
            content:
                application/json:
                    schema:
                        $ref: "#/components/schemas/SuccessApiResponse.ASC.Data.Backup.Contracts.BackupProgress"
        It will be normalized to:
            content: SuccessApiResponse.ASC.Data.Backup.Contracts.BackupProgress

        Args:
            endpoint: Endpoint to normalize
        """
        cloned_endpoint = copy.deepcopy(endpoint)

        if not cloned_endpoint or "responses" not in cloned_endpoint:
            return cloned_endpoint

        for response in cloned_endpoint["responses"].values():
            if "content" not in response:
                continue

            content = response["content"]
            if not isinstance(content, dict):
                continue

            # Process each content type
            for content_type, content_info in content.items():
                if isinstance(content_info, dict) and "schema" in content_info and "$ref" in content_info["schema"]:
                    # Extract schema name from reference
                    ref = content_info["schema"]["$ref"]
                    schema_name = ref.split("/")[-1]
                    # Replace entire content with just the schema name
                    response["content"] = schema_name
                    break  # Only need to process one content type since we're simplifying

        return cloned_endpoint

    @staticmethod
    def normalize_request_body(endpoint: EndpointInfo) -> EndpointInfo:
        """
        Normalize request body content by removing duplicate references and keeping only application/json format.
        For example, if requestBody has multiple content types with the same reference:
            content:
                text/plain: ref1
                application/json: ref1
                text/json: ref1
        It will be normalized to:
            content:
                application/json: ref1

        Args:
            endpoint: Endpoint to normalize

        Returns:
            EndpointInfo: Normalized endpoint
        """
        def simplify_schema(schema):
            """Recursively simplify schema by extracting component names from references"""
            if not isinstance(schema, dict):
                return schema

            simplified = {}
            for key, value in schema.items():
                if key == "$ref" and isinstance(value, str):
                    # Return just the component name for direct references
                    return value.split("/")[-1]
                elif key == "items" and isinstance(value, dict):
                    # Handle array items
                    simplified[key] = simplify_schema(value)
                elif key == "properties" and isinstance(value, dict):
                    # Handle object properties recursively
                    simplified[key] = {}
                    for prop_key, prop_value in value.items():
                        simplified[key][prop_key] = simplify_schema(prop_value)
                else:
                    simplified[key] = value
            return simplified

        cloned_endpoint = copy.deepcopy(endpoint)

        if "requestBody" in cloned_endpoint:
            request_body = cloned_endpoint["requestBody"]
            if not isinstance(request_body, dict):
                del cloned_endpoint["requestBody"]
                return cloned_endpoint

            # Create simplified request body with only description and content
            simplified_body = {}

            # Keep description if it exists
            if "description" in request_body:
                simplified_body["description"] = request_body["description"]

            # Extract and simplify content
            if "content" in request_body:
                content = request_body["content"]
                if isinstance(content, dict):
                    # Try to get content from application/json first, then fallback to any content
                    content_info = content.get(
                        "application/json", next(iter(content.values())) if content else None)

                    if content_info and isinstance(content_info, dict):
                        if "schema" in content_info:
                            schema = content_info["schema"]
                            simplified_body["content"] = simplify_schema(
                                schema)
                        else:
                            # Use content info directly if no schema
                            simplified_body["content"] = simplify_schema(
                                content_info)

            # Only keep request body if it has content or description
            if simplified_body:
                cloned_endpoint["requestBody"] = simplified_body
            else:
                del cloned_endpoint["requestBody"]

        # Remove empty parameters list
        if "parameters" in cloned_endpoint:
            parameters = cloned_endpoint["parameters"]
            if not parameters or (isinstance(parameters, list) and len(parameters) == 0):
                del cloned_endpoint["parameters"]

        return cloned_endpoint
