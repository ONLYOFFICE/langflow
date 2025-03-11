"""
Parser module for handling OpenAPI components.

This module provides functionality to extract and analyze component information
from OpenAPI specifications, including schemas and their dependencies.
"""

from typing import Dict, List, Set

from .types import SchemaObject, OpenAPIDocument

from .utils import extract_components, extract_component_refs


class ComponentsParser:
    """Parser for extracting and analyzing component information from OpenAPI specs."""

    @staticmethod
    def get_all_component_names(content: OpenAPIDocument) -> List[str]:
        """
        Get a list of all available component names.

        Args:
            content: Dictionary containing OpenAPI document structure

        Returns:
            List[str]: List of component names
        """
        components = extract_components(content)
        return list(components.keys())

    @staticmethod
    def get_all_components(content: OpenAPIDocument) -> Dict[str, SchemaObject]:
        """
        Get a dictionary of all components in the OpenAPI spec.

        Args:
            content: Dictionary containing OpenAPI document structure

        Returns:
            Dict[str, SchemaObject]: Dictionary mapping component names to their schemas
        """

        components: Dict[str, SchemaObject] = {}

        for component_name, component in extract_components(content).items():
            components[component_name] = component
            components[component_name]['dependencies'] = ComponentsParser.get_component_dependencies(
                content, component_name)

        components = ComponentsParser.normalize_components(components)

        return components

    @staticmethod
    def normalize_components(components: Dict[str, SchemaObject]) -> Dict[str, SchemaObject]:
        """
        Normalize component schemas by simplifying references.
        For example:
            "$ref": "#/components/schemas/ASC.Files.Core.ApiModels.ResponseDto.NewItemsDto"
        Will be simplified to:
            "$ref": "NewItemsDto"

        Args:
            components: Dictionary of components to normalize

        Returns:
            Dict[str, SchemaObject]: Normalized components
        """
        def simplify_schema(schema):
            """Recursively simplify schema by extracting component names from references"""
            if not isinstance(schema, dict):
                return schema

            simplified = {}
            for key, value in schema.items():
                if key == "$ref" and isinstance(value, str):
                    # For direct references, return just the component name
                    return value.split("/")[-1]
                elif key == "items" and isinstance(value, dict):
                    # For array items with reference, use component name directly
                    if "$ref" in value:
                        simplified[key] = value["$ref"].split("/")[-1]
                    else:
                        # For other array items, process recursively
                        simplified[key] = simplify_schema(value)
                elif key == "properties" and isinstance(value, dict):
                    # Handle object properties recursively
                    simplified[key] = {}
                    for prop_key, prop_value in value.items():
                        simplified[key][prop_key] = simplify_schema(prop_value)
                else:
                    simplified[key] = value
            return simplified

        normalized = {}
        for name, component in components.items():
            normalized[name] = simplify_schema(component)
        return normalized

    @staticmethod
    def get_component_dependencies(content: OpenAPIDocument, component_name: str, seen: Set[str] = None) -> Set[str]:
        """
        Get all dependencies for a specific component recursively.

        This includes both direct references and nested dependencies, handling circular references.

        Args:
            content: Dictionary containing OpenAPI document structure
            component_name: Name of the component to get dependencies for
            seen: Set of already processed components to prevent infinite recursion

        Returns:
            Set[str]: Set of component names that this component depends on
        """
        # Initialize seen set if not provided
        if seen is None:
            seen = set()
            
        # Prevent circular dependencies
        if component_name in seen:
            return set()
            
        seen.add(component_name)
        
        # Get all components
        components = extract_components(content)
        if component_name not in components:
            return set()

        # Get direct dependencies
        direct_deps = extract_component_refs(components[component_name])
        
        # Get recursive dependencies
        all_deps = set(direct_deps)
        for dep in direct_deps:
            if dep not in seen:
                nested_deps = ComponentsParser.get_component_dependencies(content, dep, seen)
                all_deps.update(nested_deps)
        
        return all_deps
