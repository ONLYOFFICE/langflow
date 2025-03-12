"""External authentication integration for Langflow.

This module provides integration with an external authentication system
by checking for a specific cookie and validating it against an external API.
"""

import httpx
from fastapi import Request, Response, HTTPException, status
from typing import Dict, Optional, Tuple
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession
from loguru import logger

from langflow.services.database.models.user import User, UserCreate
from langflow.services.database.models.user.crud import get_user_by_username
from langflow.services.auth.utils import get_password_hash
from langflow.initial_setup.setup import get_or_create_default_folder
from langflow.services.auth.utils import create_user_tokens
from langflow.services.deps import get_settings_service


async def verify_external_auth(request: Request, db: AsyncSession, external_api_url: Optional[str] = None) -> Tuple[Optional[User], Optional[Dict]]:
    """
    Verify external authentication by checking for asc_auth_key cookie
    and validating it against the external API.

    Args:
        request: The FastAPI request object containing cookies
        db: Database session for user operations
        external_api_url: Optional URL to use for the external API call, if None, use default

    Returns:
        Tuple containing the user (if found/created) and tokens (if authenticated)
    """
    asc_auth_key = request.cookies.get("asc_auth_key")
    if not asc_auth_key:
        return None, None

    # Use the provided external API URL or the default one
    api_url = external_api_url

    # Extract the hostname from the request to build the complete URL if needed
    if not external_api_url:
        # Get the host from the request headers or use a default
        host = request.headers.get("host", "localhost")
        protocol = "https" if request.url.scheme == "https" else "http"
        # Build the complete URL using the host from the request
        api_url = f"{protocol}://{host}/api/2.0/people/@self"

    try:
        # Call external API to validate the cookie and get user data
        async with httpx.AsyncClient() as client:
            logger.debug(f"Making external auth request to: {api_url}")
            response = await client.get(
                api_url,
                headers={"Authorization": asc_auth_key},
                follow_redirects=True
            )

            if response.status_code != 200:
                logger.warning(
                    f"External auth API returned status code {response.status_code}")
                return None, None

            response_data = response.json()

            logger.debug(f"User data from external API: {response_data}")

            user_data = response_data.get("response", {})

            # Extract user information (adjust these fields based on the actual API response)
            username = user_data.get("userName") or user_data.get("email")
            email = user_data.get("email")

            if not username or not email:
                logger.warning(
                    "External auth API did not return required user data")
                return None, None

            # Check if user exists, create if not
            existing_user = await get_user_by_username(db, username)

            if existing_user:
                # User exists, generate tokens
                tokens = await create_user_tokens(existing_user.id, db, update_last_login=True)
                return existing_user, tokens
            else:
                # Create new user
                # Generate a random password since we'll authenticate via the external system
                import secrets
                random_password = secrets.token_urlsafe(32)

                # Create new user directly using the User model (similar to add_user in the API)
                new_user = User(
                    username=username,
                    email=email,
                    password=get_password_hash(random_password),
                    is_active=True,
                    is_superuser=False  # Default to regular user
                )

                try:
                    db.add(new_user)
                    await db.commit()
                    await db.refresh(new_user)

                    # Create default folder for the user
                    folder = await get_or_create_default_folder(db, new_user.id)
                    if not folder:
                        logger.warning(
                            f"Error creating default folder for user {username}")

                    tokens = await create_user_tokens(new_user.id, db, update_last_login=True)
                    return new_user, tokens
                except Exception as e:
                    await db.rollback()
                    logger.error(
                        f"Error creating user from external auth: {str(e)}")
                    return None, None

    except Exception as e:
        logger.error(f"Error verifying external authentication: {str(e)}")
        return None, None


async def set_auth_cookies(response: Response, tokens: Dict) -> None:
    """
    Set authentication cookies in the response based on tokens.

    Args:
        response: The FastAPI response object
        tokens: Dictionary containing access_token and refresh_token
    """
    auth_settings = get_settings_service().auth_settings

    response.set_cookie(
        "refresh_token_lf",
        tokens["refresh_token"],
        httponly=auth_settings.REFRESH_HTTPONLY,
        samesite=auth_settings.REFRESH_SAME_SITE,
        secure=auth_settings.REFRESH_SECURE,
        expires=auth_settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        domain=auth_settings.COOKIE_DOMAIN,
    )

    response.set_cookie(
        "access_token_lf",
        tokens["access_token"],
        httponly=auth_settings.ACCESS_HTTPONLY,
        samesite=auth_settings.ACCESS_SAME_SITE,
        secure=auth_settings.ACCESS_SECURE,
        expires=auth_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        domain=auth_settings.COOKIE_DOMAIN,
    )
