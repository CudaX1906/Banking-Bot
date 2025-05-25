from typing import Annotated, List, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AuthState(TypedDict, total=False):
    is_authenticated: bool
    user_id: Optional[str]
    reauth_required: bool
    auth_token: Optional[str]

class ConversationState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

class OverallState(AuthState, ConversationState):
    current_intent: Optional[str]