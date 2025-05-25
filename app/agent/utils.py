from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain.agents import Tool, initialize_agent, AgentType
from ..core.config import config
from typing import List
import logging
from langchain_core.utils.function_calling import convert_to_openai_function
from typing import List, Dict, Any


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_llm():
    try:
        if not config.NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY is not set in the environment variables.")
        
        rate_limiter = InMemoryRateLimiter(
            requests_per_second=0.1,
            check_every_n_seconds=0.1,
            max_bucket_size=10,
        )

        llm = ChatNVIDIA(model="mistralai/mixtral-8x22b-instruct-v0.1",rate_limiter=rate_limiter)

        return llm
    except Exception as e:
        logger.error(f"Error creating LLM: {str(e)}")
        raise



def format_conversation(messages: list) -> str:
    from langchain_core.messages import HumanMessage, AIMessage
    lines = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            lines.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            lines.append(f"Assistant: {msg.content}")
    return "\n".join(lines)


def extract_tool_schemas(tools: List) -> Dict[str, Dict[str, Any]]:
    
    return {
        tool.name: convert_to_openai_function(tool)
        for tool in tools
    }


