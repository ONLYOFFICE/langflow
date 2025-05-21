from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import NoResultFound

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.variable import VariableCreate, VariableRead, VariableUpdate
from langflow.services.deps import get_variable_service
from langflow.services.variable.constants import CREDENTIAL_TYPE
from langflow.services.variable.service import DatabaseVariableService

router = APIRouter(prefix="/variables", tags=["Variables"])


@router.post("/", response_model=VariableRead, status_code=201)
async def create_variable(
    *,
    session: DbSession,
    variable: VariableCreate,
    current_user: CurrentActiveUser,
):
    """Create a new variable."""
    variable_service = get_variable_service()
    if not variable.name and not variable.value:
        raise HTTPException(
            status_code=400, detail="Variable name and value cannot be empty")

    if not variable.name:
        raise HTTPException(
            status_code=400, detail="Variable name cannot be empty")

    if not variable.value:
        raise HTTPException(
            status_code=400, detail="Variable value cannot be empty")

    if variable.name in await variable_service.list_variables(user_id=current_user.id, session=session):
        raise HTTPException(
            status_code=400, detail="Variable name already exists")
    try:
        return await variable_service.create_variable(
            user_id=current_user.id,
            name=variable.name,
            value=variable.value,
            default_fields=variable.default_fields or [],
            type_=variable.type or CREDENTIAL_TYPE,
            session=session,
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/", response_model=list[VariableRead], status_code=200)
async def read_variables(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
):
    """Read all variables."""
    variable_service = get_variable_service()
    if not isinstance(variable_service, DatabaseVariableService):
        msg = "Variable service is not an instance of DatabaseVariableService"
        raise TypeError(msg)
    try:
        return await variable_service.get_all(user_id=current_user.id, session=session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.patch("/{variable_id}", response_model=VariableRead, status_code=200)
async def update_variable(
    *,
    session: DbSession,
    variable_id: UUID,
    variable: VariableUpdate,
    current_user: CurrentActiveUser,
):
    """Update a variable."""
    variable_service = get_variable_service()
    if not isinstance(variable_service, DatabaseVariableService):
        msg = "Variable service is not an instance of DatabaseVariableService"
        raise TypeError(msg)
    try:
        return await variable_service.update_variable_fields(
            user_id=current_user.id,
            variable_id=variable_id,
            variable=variable,
            session=session,
        )
    except NoResultFound as e:
        raise HTTPException(
            status_code=404, detail="Variable not found") from e

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{variable_name}", response_model=VariableRead, status_code=200)
async def get_variable_by_name(
    *,
    session: DbSession,
    variable_name: str,
    current_user: CurrentActiveUser,
    include_value: bool = False,
):
    """Get a variable by name.

    Args:
        session: Database session
        variable_name: Name of the variable to retrieve
        current_user: Current authenticated user
        include_value: If True, will return the actual decrypted value for all variable types. 
                      Use with caution for credential-type variables.
    """
    variable_service = get_variable_service()
    if not isinstance(variable_service, DatabaseVariableService):
        msg = "Variable service is not an instance of DatabaseVariableService"
        raise TypeError(msg)
    try:
        variable = await variable_service.get_variable_by_name(
            user_id=current_user.id,
            name=variable_name,
            session=session,
        )
        if not variable:
            raise HTTPException(
                status_code=404, detail=f"Variable with name '{variable_name}' not found")

        # If include_value is True, we'll manually fetch and set the value
        if variable.id:
            # Query the raw variable to get the encrypted value
            from sqlmodel import select
            from langflow.services.database.models.variable.model import Variable
            from langflow.services.auth import utils as auth_utils
            from langflow.services.variable.constants import CREDENTIAL_TYPE, GENERIC_TYPE

            stmt = select(Variable).where(Variable.id == variable.id)
            db_variable = (await session.exec(stmt)).first()

            if db_variable and db_variable.value:
                # Handle based on type
                if variable.type == CREDENTIAL_TYPE:
                    # For credentials, we need to decrypt the value
                    decrypted_value = auth_utils.decrypt_api_key(
                        db_variable.value,
                        settings_service=variable_service.settings_service
                    )
                    variable.value = decrypted_value
                else:
                    # For other types (including generic), assign the value directly or decrypt if needed
                    # Some generic values might be encrypted or stored in plaintext
                    try:
                        # Try to decrypt in case it's encrypted
                        decrypted_value = auth_utils.decrypt_api_key(
                            db_variable.value,
                            settings_service=variable_service.settings_service
                        )
                        variable.value = decrypted_value
                    except Exception:
                        # If decryption fails, assume it's stored in plaintext
                        variable.value = db_variable.value

        return variable
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/{variable_id}", status_code=204)
async def delete_variable(
    *,
    session: DbSession,
    variable_id: UUID,
    current_user: CurrentActiveUser,
) -> None:
    """Delete a variable."""
    variable_service = get_variable_service()
    try:
        await variable_service.delete_variable_by_id(user_id=current_user.id, variable_id=variable_id, session=session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
