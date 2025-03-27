"""External Authentication Middleware for Langflow.

This middleware checks for the asc_auth_key cookie and authenticates users
against an external API when present.
"""

from typing import Callable, Awaitable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from sqlmodel.ext.asyncio.session import AsyncSession

from langflow.services.auth.external_auth import verify_external_auth, set_auth_cookies
from langflow.services.deps import get_session
from loguru import logger


class ExternalAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to handle external authentication via cookie and API."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def _handle_external_auth_for_refresh(self, request: Request) -> Response:
        """Handle the refresh token endpoint when using external authentication."""
        logger.debug("Handling refresh token request with external auth")

        try:
            # Get a session for database operations
            session_generator = get_session()
            session = await session_generator.__anext__()

            try:
                # Use external auth to verify and get the user
                user, tokens, chat_api_key, id_keys = await verify_external_auth(request=request, db=session)

                # If authentication succeeded, return tokens
                if user and tokens:
                    # Create a response
                    response = JSONResponse(content=tokens)

                    # Set authentication cookies including chat_api_key and chat_id_key if present
                    await set_auth_cookies(response, tokens, chat_api_key, id_keys)

                    return response
                else:
                    # Authentication failed
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "External authentication failed"}
                    )
            except Exception as e:
                logger.error(f"Error in external auth for refresh: {str(e)}")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "External authentication error"}
                )
            finally:
                # Make sure to close the session
                try:
                    await session.close()
                    # Complete the generator
                    try:
                        await session_generator.__anext__()
                    except StopAsyncIteration:
                        pass
                except Exception as e:
                    logger.error(
                        f"Error closing session in refresh handler: {str(e)}")
        except Exception as e:
            logger.error(f"Session setup error in refresh handler: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process the request, checking for external authentication."""
        # Special handling for the refresh endpoint
        if (request.url.path.endswith("/refresh") or request.url.path.endswith("/refresh/")) and "asc_auth_key" in request.cookies:
            # For refresh endpoint with asc_auth_key, always handle with our external auth
            # This ensures we don't rely on the refresh token at all when external auth is available
            return await self._handle_external_auth_for_refresh(request)

        # Skip if user is already authenticated via normal means
        if "access_token_lf" in request.cookies:
            return await call_next(request)

        # Process the request first so we don't interfere with other middleware
        response = await call_next(request)

        # Only attempt external auth if no authentication has been established
        if "access_token_lf" not in request.cookies and "asc_auth_key" in request.cookies:
            # Create a dependency manager-compatible session
            try:
                # Get a new session using FastAPI's dependency system
                # We get the generator and process it correctly
                session_generator = get_session()
                session = await session_generator.__anext__()

                try:
                    # Check for external authentication
                    user, tokens, chat_api_key, id_keys = await verify_external_auth(request, session)

                    # If we have tokens from external auth, set cookies including chat_api_key and chat_id_key if present
                    if tokens:
                        await set_auth_cookies(response, tokens, chat_api_key, id_keys)
                except Exception as e:
                    # Log the error but don't interrupt the request flow
                    from loguru import logger
                    logger.error(
                        f"Error in external auth middleware: {str(e)}")
                finally:
                    # Make sure to close the session
                    try:
                        await session.close()
                        # Complete the generator
                        try:
                            await session_generator.__anext__()
                        except StopAsyncIteration:
                            pass
                    except Exception as e:
                        from loguru import logger
                        logger.error(
                            f"Error closing session in middleware: {str(e)}")
            except Exception as e:
                from loguru import logger
                logger.error(f"Session setup error in middleware: {str(e)}")

        return response
