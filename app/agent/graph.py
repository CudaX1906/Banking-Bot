from langgraph.graph import StateGraph,START, END
from .state import OverallState
from .nodes import (
    intent_classifier,
    auth_agent,
    account_info_agent,
    transaction_agent,
    help_agent,
)

from langgraph.checkpoint.memory import InMemorySaver

from langgraph.graph import StateGraph, START, END
from typing_extensions import Literal

builder = StateGraph(OverallState)

builder.add_node(intent_classifier)
builder.add_node(auth_agent)
builder.add_node(account_info_agent)
builder.add_node(transaction_agent)
builder.add_node(help_agent)

builder.add_edge(START, "intent_classifier")


def route_by_intent(state: OverallState) -> Literal["account_info_agent", "transaction_agent", "help_agent"]:
    intent = state.get("current_intent")
    if intent == "account_info":
        return "account_info_agent"
    elif intent == "transaction":
        return "transaction_agent"
    else:
        return "help_agent"

builder.add_conditional_edges("intent_classifier", route_by_intent)

# builder.add_edge("account_info_agent", "auth_agent")
# builder.add_edge("transaction_agent", "auth_agent")

# builder.add_edge("auth_agent", "account_info_agent")
# builder.add_edge("auth_agent", "transaction_agent")

builder.add_edge("account_info_agent", END)
builder.add_edge("transaction_agent", END)
builder.add_edge("help_agent", END)

multi_agent_graph = builder.compile()  
