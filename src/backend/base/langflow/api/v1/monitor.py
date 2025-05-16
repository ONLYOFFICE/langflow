from typing import Annotated, List, Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy import delete
from sqlmodel import col, select
from pydantic import BaseModel
from loguru import logger


from langflow.api.utils import DbSession, custom_params
from langflow.services.database.models import User
from langflow.schema.message import MessageResponse, Message
from langflow.services.auth.utils import get_current_active_user
from langflow.services.database.models.message.model import MessageRead, MessageTable, MessageUpdate
from langflow.services.database.models.transactions.crud import transform_transaction_table
from langflow.services.database.models.transactions.model import TransactionTable
from langflow.services.database.models.vertex_builds.crud import (
    delete_vertex_builds_by_flow_id,
    get_vertex_builds_by_flow_id,
)
from langflow.services.database.models.vertex_builds.model import VertexBuildMapModel
from langflow.memory import aadd_messages

router = APIRouter(prefix="/monitor", tags=["Monitor"])


@router.get("/builds")
async def get_vertex_builds(flow_id: Annotated[UUID, Query()], session: DbSession) -> VertexBuildMapModel:
    try:
        vertex_builds = await get_vertex_builds_by_flow_id(session, flow_id)
        return VertexBuildMapModel.from_list_of_dicts(vertex_builds)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/builds", status_code=204)
async def delete_vertex_builds(flow_id: Annotated[UUID, Query()], session: DbSession) -> None:
    try:
        await delete_vertex_builds_by_flow_id(session, flow_id)
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/messages")
async def get_messages(
    session: DbSession,
    flow_id: Annotated[UUID | None, Query()] = None,
    session_id: Annotated[str | None, Query()] = None,
    sender: Annotated[str | None, Query()] = None,
    sender_name: Annotated[str | None, Query()] = None,
    order_by: Annotated[str | None, Query()] = "timestamp",
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
) -> list[MessageResponse]:
    try:
        stmt = select(MessageTable)
        logger.debug("Current flow_id: {}", flow_id)
        logger.debug("Current session_id: {}", session_id)
        logger.debug("Current sender: {}", sender)
        logger.debug("Current sender_name: {}", sender_name)
        logger.debug("Current order_by: {}", order_by)
        if flow_id:
            flow_uuid = flow_id if isinstance(
                flow_id, UUID) else UUID(str(flow_id))
            stmt = stmt.where(MessageTable.flow_id == flow_uuid)
        if session_id:
            # Check if session_id is in the format '/d/X' or just a numeric value
            if session_id.isdigit():
                # If session_id is numeric, treat it as folder ID
                folder_prefix = f"folder-{session_id}-{str(current_user.id)}"
                logger.debug(f"Folder prefix: {folder_prefix}")
                # Output the user ID for debugging
                logger.debug(f"Current user ID for prefix: {current_user.id}")

                # First, check if any matching sessions exist (for debugging)
                check_stmt = select(MessageTable.session_id).where(
                    MessageTable.session_id.startswith(folder_prefix))
                sample_sessions = await session.exec(check_stmt)
                sample_sessions_list = sample_sessions.all()
                logger.debug(
                    f"Found {len(sample_sessions_list)} sessions matching prefix {folder_prefix}")
                if sample_sessions_list:
                    logger.debug(
                        f"Sample matching session: {sample_sessions_list[0]}")

                # Filter for session_ids starting with this prefix
                stmt = stmt.where(
                    MessageTable.session_id.startswith(folder_prefix))
                logger.debug(
                    f"Numeric session_id detected, filtering for session_id starting with: {folder_prefix}")
            else:
                # Default behavior (exact match) for other session_id formats
                stmt = stmt.where(MessageTable.session_id == session_id)
        if sender:
            stmt = stmt.where(MessageTable.sender == sender)
        if sender_name:
            stmt = stmt.where(MessageTable.sender_name == sender_name)
        if order_by:
            col = getattr(MessageTable, order_by).asc()
            stmt = stmt.order_by(col)
        messages = await session.exec(stmt)
        return [MessageResponse.model_validate(d, from_attributes=True) for d in messages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/messages", status_code=204, dependencies=[Depends(get_current_active_user)])
async def delete_messages(message_ids: list[UUID], session: DbSession) -> None:
    try:
        # type: ignore[attr-defined]
        await session.exec(delete(MessageTable).where(MessageTable.id.in_(message_ids)))
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/messages/{message_id}", dependencies=[Depends(get_current_active_user)], response_model=MessageRead)
async def update_message(
    message_id: UUID,
    message: MessageUpdate,
    session: DbSession,
):
    try:
        db_message = await session.get(MessageTable, message_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")

    try:
        message_dict = message.model_dump(
            exclude_unset=True, exclude_none=True)
        if "text" in message_dict and message_dict["text"] != db_message.text:
            message_dict["edit"] = True
        db_message.sqlmodel_update(message_dict)
        session.add(db_message)
        await session.commit()
        await session.refresh(db_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return db_message


@router.patch(
    "/messages/session/{old_session_id}",
    dependencies=[Depends(get_current_active_user)],
)
async def update_session_id(
    old_session_id: str,
    new_session_id: Annotated[str, Query(..., description="The new session ID to update to")],
    session: DbSession,
) -> list[MessageResponse]:
    try:
        # Get all messages with the old session ID
        stmt = select(MessageTable).where(
            MessageTable.session_id == old_session_id)
        messages = (await session.exec(stmt)).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    if not messages:
        raise HTTPException(
            status_code=404, detail="No messages found with the given session ID")

    try:
        # Update all messages with the new session ID
        for message in messages:
            message.session_id = new_session_id

        session.add_all(messages)

        await session.commit()
        message_responses = []
        for message in messages:
            await session.refresh(message)
            message_responses.append(
                MessageResponse.model_validate(message, from_attributes=True))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return message_responses


@router.delete("/messages/session/{session_id}", status_code=204)
async def delete_messages_session(
    session_id: str,
    session: DbSession,
):
    try:
        await session.exec(
            delete(MessageTable)
            .where(col(MessageTable.session_id) == session_id)
            .execution_options(synchronize_session="fetch")
        )
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return {"message": "Messages deleted successfully"}


# Define a simple request model with only the essential fields
class SimpleMessageRequest(BaseModel):
    text: str
    sender: str
    sender_name: str
    session_id: str
    flow_id: Optional[UUID] = None


@router.post("/messages", dependencies=[Depends(get_current_active_user)])
async def add_messages(
    message_data: Annotated[SimpleMessageRequest, Body(...)],
) -> list[MessageResponse]:
    """Add a message to the database with only essential fields.

    This simplified endpoint accepts only the basic required fields
    (text, sender, sender_name, session_id, flow_id) and creates a proper
    Message object to store in the database.

    Returns the stored message with its ID and timestamp.
    """
    try:
        # Create a new Message object with the provided data
        message = Message(
            text=message_data.text,
            sender=message_data.sender,
            sender_name=message_data.sender_name,
            session_id=message_data.session_id,
        )

        # If flow_id was provided in the request, use it
        if message_data.flow_id:
            message.flow_id = message_data.flow_id

        # Add the message to the database
        stored_messages = await aadd_messages(message, flow_id=message_data.flow_id)

        # Convert the stored messages to proper response objects
        # This will ensure the timestamp is properly formatted for the response
        response_messages = []
        for msg in stored_messages:
            # Convert the message to dict and manually parse the timestamp
            msg_dict = msg.model_dump()
            if "timestamp" in msg_dict and isinstance(msg_dict["timestamp"], str):
                # Remove the UTC timezone name which causes validation errors
                if "UTC" in msg_dict["timestamp"]:
                    msg_dict["timestamp"] = datetime.fromisoformat(
                        msg_dict["timestamp"].replace(" UTC", "").strip()
                    )
            # Create a MessageResponse from the cleaned dict
            response_messages.append(MessageResponse.model_validate(msg_dict))

        return response_messages
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception(f"Error adding message: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/transactions")
async def get_transactions(
    flow_id: Annotated[UUID, Query()],
    session: DbSession,
    params: Annotated[Params | None, Depends(custom_params)],
) -> Page[TransactionTable]:
    try:
        stmt = (
            select(TransactionTable)
            .where(TransactionTable.flow_id == flow_id)
            .order_by(col(TransactionTable.timestamp))
        )
        return await paginate(session, stmt, params=params, transformer=transform_transaction_table)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
