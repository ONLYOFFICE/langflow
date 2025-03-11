"""
Parser module for handling OpenAPI tags.

This module provides functionality to extract and analyze tag information
from OpenAPI specifications.
"""

from typing import List

from .types import OpenAPIDocument, TagInfo

from .utils import extract_tags


class TagsParser:
    """Parser for extracting and analyzing tag information from OpenAPI specs."""

    @staticmethod
    def get_all_tag_names(content: OpenAPIDocument) -> List[str]:
        """
        Get a list of all available tag names.

        Args:
            content: Dictionary containing OpenAPI document structure

        Returns:
            List[str]: List of tag names
        """
        tags = extract_tags(content)
        return list(tags.keys())

    @staticmethod
    def get_all_tags(content: OpenAPIDocument) -> List[TagInfo]:
        """
        Get a list of all available tag details.

        Args:
            content: Dictionary containing OpenAPI document structure

        Returns:
            List[TagInfo]: List of tag details
        """
        tags = extract_tags(content)

        return list(tags.values())
