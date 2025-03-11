from copy import deepcopy
from json import JSONEncoder
from enum import Enum

from typing import Dict, Any, Optional, Tuple

from .components import ComponentsParser
from .tags import TagsParser
from .endpoints import EndpointsParser


class SetEncoder(JSONEncoder):
    """Custom JSON encoder that converts sets to lists"""

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return JSONEncoder.default(self, obj)


class DocType(Enum):
    """Type of documentation format."""
    OPENAPI = "openapi"
    TYPEDOC = "typedoc"
    UNKNOWN = "unknown"


class Parser:
    """Main parser for documentation files.

    This class detects the type of documentation (OpenAPI or TypeDoc)
    and delegates parsing to the appropriate specialized parser.
    """

    @staticmethod
    def detect_doc_type(content: Any) -> DocType:
        """Detect the type of documentation from its content.

        Args:
            content: The parsed content from JSON/YAML file

        Returns:
            DocType: The detected documentation type
        """
        if not isinstance(content, dict):
            return DocType.UNKNOWN

        # Check for TypeDoc indicators
        if all(key in content for key in ["id", "name", "kind", "variant"]):
            return DocType.TYPEDOC

        # Check for OpenAPI indicators
        if any(key in content for key in ["swagger", "openapi"]):
            return DocType.OPENAPI

        return DocType.UNKNOWN

    @staticmethod
    def validate_openapi_params(content: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate that required OpenAPI parameters are present.

        Args:
            content: The parsed OpenAPI content

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        required_fields = ["paths"]
        missing_fields = [
            field for field in required_fields if field not in content]

        if missing_fields:
            return False, f"Missing required OpenAPI fields: {', '.join(missing_fields)}"

        # Check paths structure
        paths = content.get("paths", {})
        if not isinstance(paths, dict):
            return False, "OpenAPI paths must be an object"

        # Check for at least one valid path
        for path, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            for method in methods:
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    return True, None

        return False, "No valid HTTP methods found in paths"

    @staticmethod
    def parse(content: Any) -> Dict[str, Any]:
        """Parse documentation content based on its detected type.

        Args:
            content: The parsed content from JSON/YAML file

        Returns:
            Dict[str, Any]: Structured documentation data

        Raises:
            ValueError: If content type cannot be determined or is invalid
        """
        doc_type = Parser.detect_doc_type(content)

        if doc_type == DocType.OPENAPI:
            # Validate OpenAPI structure
            is_valid, error = Parser.validate_openapi_params(content)
            if not is_valid:
                raise ValueError(f"Invalid OpenAPI content: {error}")

            # Parse using OpenAPI parser
            tags = TagsParser.get_all_tags(content)
            endpoints = EndpointsParser.get_all_endpoints_info(content)
            components = ComponentsParser.get_all_components(content)

            for endpoint_name, endpoint in endpoints.items():
                endpoint_components = endpoint.get("dependencies", {})
                for component_name in endpoint_components:
                    component = components.get(component_name)
                    if component is not None:
                        endpoints[endpoint_name]["dependencies"] = endpoint["dependencies"].union(
                            component["dependencies"])

            for endpoint_name, endpoint in endpoints.items():
                endpoint["components"] = {}
                if endpoint["dependencies"]:
                    for component_name in endpoint["dependencies"]:
                        if component_name not in components:
                            raise ValueError(
                                f"Component {component_name} not found in components")

                        current_component = deepcopy(
                            components[component_name])
                        del current_component['dependencies']
                        del current_component['version']
                        endpoint["components"][component_name] = current_component

            return {
                "type": "openapi",
                "endpoints": endpoints,
                "tags": tags,
                "components": components
            }

        else:
            raise ValueError("Unknown documentation type")
