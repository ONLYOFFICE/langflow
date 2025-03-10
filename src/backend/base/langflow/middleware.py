"""Middleware module for Langflow (legacy import).

This file maintains backward compatibility with the old middleware module structure.
New code should import directly from the middleware package.
"""

from langflow.middleware.content_size_limit import MaxFileSizeException, ContentSizeLimitMiddleware
from langflow.middleware.external_auth_middleware import ExternalAuthMiddleware

__all__ = ["MaxFileSizeException", "ContentSizeLimitMiddleware", "ExternalAuthMiddleware"]
