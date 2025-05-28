from langsmith import traceable
from .state import OverallState
from langgraph.graph import END
from langgraph.types import Command,interrupt
from langchain_core.messages import AIMessage,HumanMessage
from typing import Annotated, Literal
from .utils import create_llm,format_conversation,extract_tool_schemas
from app.schemas import FunctionCallPayload
from app.shared import client
from .prompts import TOOL_CALLING_PROMPT
from app.agent.tools import (
    create_transaction_tool,create_account,get_account_info,update_account_info,delete_account,get_transaction_tool,list_transactions_by_account_tool)
import json

@traceable(client=client, project_name="bank-bot",name="intent-classify", run_type="chain")
async def intent_classifier(state: OverallState) -> Command[Literal["account_info_agent", "transaction_agent", "help_agent", "__end__"]]:
    """
    Classify the user's intent based on the conversation state.
    Returns a command to route to the appropriate agent or end the conversation.
    """

    
    last_user_msg = next((m for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), None)


    if not last_user_msg:
        return Command(goto="__end__")

    prompt = f"""
    Classify the user's intent into one of the following categories: account_info, transaction, help.
    User query: "{last_user_msg.content}"
    Respond with only one of: account_info, transaction, help.
    """
    llm = create_llm()
    response = await llm.ainvoke([{"role": "user", "content": prompt}])
    intent = response.content.strip().lower()

    valid_intents = {"account_info", "transaction", "help"}
    if intent not in valid_intents:
        intent = "help"

    next_agent = f"{intent}_agent"

    classification_msg = AIMessage(content=f"Intent classified as '{intent}'. Routing to {next_agent}.")
    updated_messages = state["messages"] + [classification_msg]

    return Command(goto=next_agent, update={"messages": updated_messages, "current_intent": intent})

@traceable(client=client, project_name="bank-bot", name="auth", run_type="chain")
async def auth_agent(state: OverallState) -> Command:
    print("Running auth_agent with state:", state)
    if state.get("is_authenticated") and not state.get("reauth_required"):
        intent = state.get("current_intent")
        if intent == "account_info":
            return Command(goto="account_info_agent")
        elif intent == "transaction":
            return Command(goto="transaction_agent")
        else:
            return Command(goto="__end__")

    # Simulate OTP verification success
    updated_state = {
        "is_authenticated": True,
        "reauth_required": False,
        "messages": state["messages"] + [
            HumanMessage(content="Simulated OTP: 123456"),
            AIMessage(content="OTP verified successfully."),
        ],
    }
    intent = state.get("current_intent")
    next_agent = "account_info_agent" if intent == "account_info" else "transaction_agent"
    
    return Command(goto=next_agent, update=updated_state)


@traceable(client=client, project_name="bank-bot", name="account-info", run_type="chain")
async def account_info_agent(state: OverallState) -> Command[Literal["auth_agent", "__end__"]]:

    
    if not state.get("is_authenticated") or state.get("reauth_required"):
        return Command(goto="auth_agent")

    tools = [create_account, get_account_info, update_account_info, delete_account]
    llm = create_llm()
    tool_schemas = extract_tool_schemas(tools)

    prompt = TOOL_CALLING_PROMPT.format(
        tool_schemas_json=json.dumps(tool_schemas),
        chat_history=format_conversation(state["messages"]),
        user_input=state["messages"][-1].content
    )

    # structured_llm = llm.with_structured_output(FunctionCallPayload)
    response = await llm.ainvoke([{"role": "user", "content": prompt}])
    response = FunctionCallPayload.model_validate_json(response.content)
    print("LLM response:", response)
    tool_names = [tool.name for tool in tools]

    if (
        response.tool is None
        or response.tool not in tool_names
        or set(response.missing) - {"token"}
    ):
        error_msg = AIMessage(content="Please try again. The info you provided is not sufficient to process your request.")
        updated_state = {
            "messages": state["messages"] + [error_msg],
            "last_agent_response": error_msg.content,
        }
        return Command(goto="__end__", update=updated_state)
    
     


    response.provided["token"] = state.get("auth_token")
    print(response)
    tool_map = {tool.name: tool for tool in tools}
    tool_fn = tool_map[response.tool]
    result = await tool_fn.ainvoke(response.provided)

    response_msg = AIMessage(content=str(result))

    updated_state = {
        "messages": state["messages"] + [response_msg]
    }

    return Command(goto="__end__", update=updated_state)



@traceable(client=client, project_name="bank-bot", name="transaction", run_type="chain")
async def transaction_agent(state: OverallState) -> Command[Literal["auth_agent", "__end__"]]:
    if state.get("current_intent") != "transaction":
        return Command(goto="__end__")
    if not state.get("is_authenticated") or state.get("reauth_required"):
        return Command(goto="auth_agent")

    tools = [
        create_transaction_tool,
        list_transactions_by_account_tool,
        get_transaction_tool,
    ]

    llm = create_llm()
    tool_schemas = extract_tool_schemas(tools)

    prompt = TOOL_CALLING_PROMPT.format(
        tool_schemas_json=json.dumps(tool_schemas),
        chat_history=format_conversation(state["messages"]),
        user_input=state["messages"][-1].content
    )

    # structured_llm = llm.with_structured_output(FunctionCallPayload)
    response = await llm.ainvoke([{"role": "user", "content": prompt}])
    response = FunctionCallPayload.model_validate_json(response.content)
    print("LLM response:", response)
    tool_names = [tool.name for tool in tools]

    if (
        response.tool is None
        or response.tool not in tool_names
        or set(response.missing) - {"token"}
    ):
        error_msg = AIMessage(content="Please try again. The info you provided is not sufficient to process your request.")
        updated_state = {
            "messages": state["messages"] + [error_msg],
        }
        return Command(goto="__end__", update=updated_state)
    


    response.provided["token"] = state.get("auth_token")
    print(response)
    tool_map = {tool.name: tool for tool in tools}
    tool_fn = tool_map[response.tool]
    result = await tool_fn.ainvoke(response.provided)

    response_msg = AIMessage(content=str(result))


    updated_state = {
        "messages": state["messages"] + [response_msg],
    }
    return Command(goto="__end__", update=updated_state)


@traceable(client=client, project_name="bank-bot",name="support", run_type="chain")
async def help_agent(state: OverallState) -> Command[Literal["__end__"]]:
    response = AIMessage(content="How can I assist you? You can ask about your account or transactions.")
    updated_state = {
        "messages": state["messages"] + [response],
        "last_agent_response": response.content,
    }
    return Command(goto="__end__", update=updated_state)


