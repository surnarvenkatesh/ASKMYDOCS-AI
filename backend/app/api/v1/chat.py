"""
Chat endpoints — conversation management and the streaming RAG chat
endpoint. Streaming uses Server-Sent Events: the client gets a series of
`data: {...}\\n\\n` frames — one per generated token, then a final
`citations` frame and a `done` frame.
"""
import uuid
from typing import Annotated

import orjson
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_chat_service,
    get_conversation_repository,
    get_current_user,
)
from app.core.database import get_db
from app.models.conversation import Conversation
from app.models.user import User
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.chat import (
    ChatRequest,
    ConversationCreate,
    ConversationDetailRead,
    ConversationRead,
    ConversationRenameRequest,
)
from app.services.chat_service import ChatService, ChatServiceError

router = APIRouter(prefix="/chat", tags=["Chat"])


async def _get_owned_conversation(
    conversation_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    conversation_repository: Annotated[ConversationRepository, Depends(get_conversation_repository)],
) -> Conversation:
    conversation = await conversation_repository.get_by_id(conversation_id, owner_id=current_user.id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


@router.post(
    "/conversations",
    response_model=ConversationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new conversation",
)
async def create_conversation(
    body: ConversationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    conversation_repository: Annotated[ConversationRepository, Depends(get_conversation_repository)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Conversation:
    conversation = await conversation_repository.create(
        current_user.id, title=body.title or "New conversation"
    )
    await db.commit()
    return conversation


@router.get(
    "/conversations",
    response_model=list[ConversationRead],
    summary="List my conversations",
)
async def list_conversations(
    current_user: Annotated[User, Depends(get_current_user)],
    conversation_repository: Annotated[ConversationRepository, Depends(get_conversation_repository)],
) -> list[Conversation]:
    return await conversation_repository.list_for_owner(current_user.id)


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailRead,
    summary="Get a conversation with its full message history",
)
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    conversation_repository: Annotated[ConversationRepository, Depends(get_conversation_repository)],
) -> Conversation:
    conversation = await conversation_repository.get_with_messages(conversation_id, owner_id=current_user.id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


@router.patch(
    "/conversations/{conversation_id}",
    response_model=ConversationRead,
    summary="Rename a conversation",
)
async def rename_conversation(
    body: ConversationRenameRequest,
    conversation: Annotated[Conversation, Depends(_get_owned_conversation)],
    conversation_repository: Annotated[ConversationRepository, Depends(get_conversation_repository)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Conversation:
    updated = await conversation_repository.rename(conversation, body.title)
    await db.commit()
    return updated


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation",
)
async def delete_conversation(
    conversation: Annotated[Conversation, Depends(_get_owned_conversation)],
    conversation_repository: Annotated[ConversationRepository, Depends(get_conversation_repository)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await conversation_repository.delete(conversation)
    await db.commit()


@router.post(
    "/conversations/{conversation_id}/messages",
    summary="Ask a question in this conversation (streams the answer as Server-Sent Events)",
)
async def send_message(
    body: ChatRequest,
    conversation: Annotated[Conversation, Depends(_get_owned_conversation)],
    current_user: Annotated[User, Depends(get_current_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StreamingResponse:
    async def event_stream():
        try:
            async for event in chat_service.answer_stream(
                owner_id=current_user.id,
                conversation_id=conversation.id,
                question=body.question,
                document_ids=body.document_ids,
            ):
                payload = {
                    "type": event.type,
                    "text": event.text,
                    "citations": event.citations,
                    "metadata": event.metadata,
                }
                yield f"data: {orjson.dumps(payload).decode()}\n\n"
            await db.commit()
        except ChatServiceError as exc:
            await db.rollback()
            error_payload = {"type": "error", "text": str(exc), "citations": [], "metadata": {}}
            yield f"data: {orjson.dumps(error_payload).decode()}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
