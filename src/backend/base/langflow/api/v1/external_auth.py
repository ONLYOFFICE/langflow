"""External authentication endpoints for Langflow.

This module provides endpoints to handle authentication from external systems.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from typing import Optional, Dict, Any

from langflow.api.utils import DbSession
from langflow.api.v1.schemas import Token
from langflow.services.auth.external_auth import verify_external_auth, set_auth_cookies
from langflow.services.deps import get_settings_service

router = APIRouter(tags=["External Authentication"])


@router.get("/external-login", response_model=Token)
async def login_with_external_credentials(
    request: Request,
    response: Response,
    db: DbSession,
    external_api_url: Optional[str] = None,
):
    """
    Authenticate using credentials from an external system.
    
    This endpoint checks for the asc_auth_key cookie and validates it against
    the external API. If valid, it creates a user (if new) or logs in an existing user.
    
    Args:
        request: The FastAPI request object
        response: The FastAPI response object for setting cookies
        db: Database session
        external_api_url: Optional override for the external API URL
        
    Returns:
        Token object with access and refresh tokens
    """
    # Check for external authentication cookie
    auth_cookie = request.cookies.get("asc_auth_key")
    if not auth_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No external authentication cookie found",
        )
    
    # Attempt to verify with the external system and get user info
    user, tokens, chat_api_key, chat_id_key = await verify_external_auth(
        request=request, 
        db=db, 
        external_api_url=external_api_url
    )
    
    if not user or not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="External authentication failed",
        )
    
    # Set authentication cookies in the response including chat_api_key and chat_id_key if present
    await set_auth_cookies(response, tokens, chat_api_key, chat_id_key)
    
    return tokens


@router.get("/external-auth-status")
async def check_external_auth_status(request: Request) -> Dict[str, Any]:
    """
    Check if external authentication is available based on cookie presence.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        Dictionary with status information
    """
    auth_cookie = request.cookies.get("asc_auth_key")
    return {
        "external_auth_available": auth_cookie is not None,
        "cookie_exists": auth_cookie is not None
    }
