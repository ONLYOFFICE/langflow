from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from langflow.api.utils import DbSession
from langflow.api.v1.schemas import Token
from langflow.initial_setup.setup import get_or_create_default_folder
from langflow.services.auth.utils import (
    authenticate_user,
    create_refresh_token,
    create_user_longterm_token,
    create_user_tokens,
)
from langflow.services.database.models.user.crud import get_user_by_id
from langflow.services.deps import get_settings_service, get_variable_service

router = APIRouter(tags=["Login"])


@router.post("/login", response_model=Token)
async def login_to_get_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
):
    auth_settings = get_settings_service().auth_settings
    try:
        user = await authenticate_user(form_data.username, form_data.password, db)
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    if user:
        tokens = await create_user_tokens(user_id=user.id, db=db, update_last_login=True)
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
        response.set_cookie(
            "apikey_tkn_lflw",
            str(user.store_api_key),
            httponly=auth_settings.ACCESS_HTTPONLY,
            samesite=auth_settings.ACCESS_SAME_SITE,
            secure=auth_settings.ACCESS_SECURE,
            expires=None,  # Set to None to make it a session cookie
            domain=auth_settings.COOKIE_DOMAIN,
        )
        await get_variable_service().initialize_user_variables(user.id, db)
        # Create default project for user if it doesn't exist
        _ = await get_or_create_default_folder(db, user.id)
        return tokens
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/auto_login")
async def auto_login(request: Request, response: Response, db: DbSession):
    auth_settings = get_settings_service().auth_settings

    # Extract request origin information
    origin = request.headers.get("Origin", "")

    # If origin is missing, use the request's scheme and host
    if not origin:
        request_scheme = request.url.scheme
        request_host = request.headers.get("host") or request.url.netloc
        request_origin = f"{request_scheme}://{request_host}"
    else:
        request_origin = origin

    # Log the request origin
    from loguru import logger
    logger.debug(f"Auto login request from origin: {request_origin}")


    # Check for external authentication via asc_auth_key cookie
    if "asc_auth_key" in request.cookies:
        from langflow.services.auth.external_auth import verify_external_auth, set_auth_cookies

        try:
            logger.debug("Auto login with external authentication")
            user, tokens, chat_api_key = await verify_external_auth(request=request, db=db)

            logger.debug(f"User: {user}")
            logger.debug(f"Tokens: {tokens}")

            if user and tokens:
                # Save the asc_auth_key to the database for the current user as a variable
                asc_auth_key = request.cookies.get("asc_auth_key")
                if asc_auth_key:
                    from langflow.services.deps import get_variable_service
                    from langflow.services.variable.constants import CREDENTIAL_TYPE

                    logger.debug(f"Saving asc_auth_key for user {user.id}")
                    variable_service = get_variable_service()

                    # Check if variable already exists for this user
                    existing_variables = await variable_service.list_variables(user_id=user.id, session=db)

                    if "asc_auth_key" in existing_variables:
                        # Update existing variable
                        await variable_service.update_variable(
                            user_id=user.id,
                            name="asc_auth_key",
                            value=asc_auth_key,
                            session=db
                        )
                        logger.debug(
                            f"Updated asc_auth_key variable for user {user.id}")
                    else:
                        # Create new variable
                        await variable_service.create_variable(
                            user_id=user.id,
                            name="asc_auth_key",
                            value=asc_auth_key,
                            type_=CREDENTIAL_TYPE,
                            session=db
                        )
                        logger.debug(
                            f"Created asc_auth_key variable for user {user.id}")

                    # Save request origin information
                    if "portal_origin" in existing_variables:
                        await variable_service.update_variable(
                            user_id=user.id,
                            name="portal_origin",
                            value=request_origin,
                            session=db
                        )
                        logger.debug(
                            f"Updated portal_origin variable for user {user.id}")
                    else:
                        await variable_service.create_variable(
                            user_id=user.id,
                            name="portal_origin",
                            value=request_origin,
                            type_="str",
                            session=db
                        )
                        logger.debug(
                            f"Created portal_origin variable for user {user.id}")

                # Save the OPENAI_API_KEY from environment variables to the user variables
                import os
                OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
                if OPENAI_API_KEY:
                    # We already imported the variable service earlier
                    if not 'variable_service' in locals():
                        from langflow.services.deps import get_variable_service
                        from langflow.services.variable.constants import CREDENTIAL_TYPE
                        variable_service = get_variable_service()

                    # Check if openai_api_key already exists for this user
                    if not 'existing_variables' in locals():
                        existing_variables = await variable_service.list_variables(user_id=user.id, session=db)

                    if "openai_api_key" in existing_variables:
                        # Update existing variable
                        await variable_service.update_variable(
                            user_id=user.id,
                            name="openai_api_key",
                            value=OPENAI_API_KEY,
                            session=db
                        )
                        logger.debug(
                            f"Updated openai_api_key variable for user {user.id}")
                    else:
                        # Create new variable
                        await variable_service.create_variable(
                            user_id=user.id,
                            name="openai_api_key",
                            value=OPENAI_API_KEY,
                            type_=CREDENTIAL_TYPE,
                            session=db
                        )
                        logger.debug(
                            f"Created openai_api_key variable for user {user.id}")

                # Set authentication cookies including chat_api_key and chat_id_key if present
                await set_auth_cookies(response, tokens, chat_api_key)

                # Set API key cookie if available
                if user.store_api_key is not None:
                    response.set_cookie(
                        "apikey_tkn_lflw",
                        str(user.store_api_key),  # Ensure it's a string
                        httponly=auth_settings.ACCESS_HTTPONLY,
                        samesite=auth_settings.ACCESS_SAME_SITE,
                        secure=auth_settings.ACCESS_SECURE,
                        expires=None,  # Set to None to make it a session cookie
                        domain=auth_settings.COOKIE_DOMAIN,
                    )

                return tokens
        except Exception as e:
            logger.error(f"Error in external auto login: {str(e)}")
            # Fall through to regular auto login if external auth fails

    # Fall back to standard auto login
    if auth_settings.AUTO_LOGIN:
        user_id, tokens = await create_user_longterm_token(db)
        response.set_cookie(
            "access_token_lf",
            tokens["access_token"],
            httponly=auth_settings.ACCESS_HTTPONLY,
            samesite=auth_settings.ACCESS_SAME_SITE,
            secure=auth_settings.ACCESS_SECURE,
            expires=None,  # Set to None to make it a session cookie
            domain=auth_settings.COOKIE_DOMAIN,
        )

        user = await get_user_by_id(db, user_id)

        if user:
            if user.store_api_key is None:
                user.store_api_key = ""

            response.set_cookie(
                "apikey_tkn_lflw",
                str(user.store_api_key),  # Ensure it's a string
                httponly=auth_settings.ACCESS_HTTPONLY,
                samesite=auth_settings.ACCESS_SAME_SITE,
                secure=auth_settings.ACCESS_SECURE,
                expires=None,  # Set to None to make it a session cookie
                domain=auth_settings.COOKIE_DOMAIN,
            )

        return tokens

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "message": "Auto login is disabled. Please enable it in the settings",
            "auto_login": False,
        },
    )


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    db: DbSession,
):
    auth_settings = get_settings_service().auth_settings

    token = request.cookies.get("refresh_token_lf")

    if token:
        tokens = await create_refresh_token(token, db)
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
        return tokens
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token_lf")
    response.delete_cookie("access_token_lf")
    response.delete_cookie("apikey_tkn_lflw")
    return {"message": "Logout successful"}
