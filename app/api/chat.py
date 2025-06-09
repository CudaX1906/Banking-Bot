from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from app.db.models import Message, User, ChatSession
from app.db.database import get_db
import asyncio
from app.api.user import get_current_user
from app.api.sessions import get_current_session
from app.schemas import ChatQuery
from app.db.schemas import SenderEnum
from uuid import UUID
from app.core.redis_client import redis_client
from app.agent.graph import multi_agent_graph
import json

router = APIRouter(prefix="/chat", tags=["Chat"])


# Load conversation history from Redis (fallback logic can be added later if needed)
async def load_conversation_history(user_id: UUID, session_id: UUID) -> list[BaseMessage]:
    redis_key = f"chat:history:{user_id}:{session_id}"
    history_json = await redis_client.get(redis_key)

    history = []
    if history_json:
        history_data = json.loads(history_json)
        for msg in history_data:
            if msg["sender"] == "user":
                history.append(HumanMessage(content=msg["content"]))
            else:
                history.append(AIMessage(content=msg["content"]))
    return history


# Save full conversation history to Redis
async def save_conversation_to_redis(user_id: UUID, session_id: UUID, history: list[BaseMessage]):
    redis_key = f"chat:history:{user_id}:{session_id}"
    history_data = []
    for msg in history:
        history_data.append({
            "sender": "user" if isinstance(msg, HumanMessage) else "bot",
            "content": msg.content,
        })
    await redis_client.set(redis_key, json.dumps(history_data))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def chat_endpoint(
    chat_query: ChatQuery,
    session: ChatSession = Depends(get_current_session),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):  
    query = chat_query.query
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    key = f"user:{current_user.user_id}:auth_token"
    token = await redis_client.get(key)

    conversation_history = await load_conversation_history(current_user.user_id, session.session_id)

    
    conversation_history.append(HumanMessage(content=query))

    
    state = {
        "messages": conversation_history,
        "is_authenticated": getattr(current_user, "is_authenticated", False),
        "user_id": current_user.user_id,
        "reauth_required": False,
        "auth_token": token,
        "current_intent": None,
    }

    
    result = await multi_agent_graph.ainvoke(
        state,
        config={
            "configurable": {
                "user_id": current_user.user_id,
                "session_id": str(session.session_id),
                "thread_id": "bankbot"
            }
        },
    )

    
    ai_response = None
    if "messages" in result and len(result["messages"]) > len(conversation_history):
        ai_response = result["messages"][-1].content

    
    def save_messages():
        user_msg = Message(
            session_id=session.session_id,
            content=query,
            sender=SenderEnum.user,
            timestamp=datetime.utcnow(),
        )
        db.add(user_msg)

        ai_msg = None
        if ai_response:
            ai_msg = Message(
                session_id=session.session_id,
                content=ai_response,
                sender=SenderEnum.bot,
                timestamp=datetime.utcnow(),
            )
            db.add(ai_msg)

        db.commit()
        db.refresh(user_msg)
        if ai_msg:
            db.refresh(ai_msg)

        return user_msg, ai_msg

    user_msg, ai_msg = await asyncio.to_thread(save_messages)

    # Save updated conversation to Redis
    await save_conversation_to_redis(current_user.user_id, session.session_id, result["messages"])

    return {
        "user_message_id": user_msg.message_id,
        "ai_response": ai_response,
    }
