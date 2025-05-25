from langchain.tools import tool
import httpx
from typing import Optional
from app.core.config import config

API_BASE_URL = config.API_BASE_URL

@tool
async def create_account(name: str, currency: str, account_type: str, balance: float, token: str) -> str:
    """
    Create a new account for the current user.
    Requires: name, currency, account_type, initial balance, and authorization token.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/account/create",
            json={
                "name": name,
                "currency": currency,
                "account_type": account_type,
                "balance": balance,
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 201:
            return f"Account created successfully: {response.json()}"
        return f"Failed to create account: {response.text}"

@tool
async def get_account_info(token: str) -> str:
    """
    Get account information for the current user.
    Requires: authorization token.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/account/info",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return f"Account info: {response.json()}"
        return f"Failed to retrieve account info: {response.text}"

@tool
async def update_account_info(update_data: dict, token: str) -> str:
    """
    Update the current user's account information.
    Requires: update fields as a dictionary and authorization token.
    """
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{API_BASE_URL}/account/update",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return f"Account updated: {response.json()}"
        return f"Failed to update account: {response.text}"

@tool
async def delete_account(token: str) -> str:
    """
    Deactivate the current user's account.
    Requires: authorization token.
    """
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{API_BASE_URL}/account/delete",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 204:
            return "Account deleted successfully."
        return f"Failed to delete account: {response.text}"

# @tool
# async def get_account_balance(token: str) -> str:
#     """
#     Get the account balance for the current user.
#     Requires: authorization token.
#     """
#     async with httpx.AsyncClient() as client:
#         response = await client.get(
#             f"{API_BASE_URL}/info",
#             headers={"Authorization": f"Bearer {token}"}
#         )
#         if response.status_code == 200:
#             data = response.json()
#             return f"Account balance is {data['balance']} {data['currency']}"
#         return f"Failed to retrieve account balance: {response.text}"


@tool
async def create_transaction_tool(from_account: str, to_account: str, amount: float, token: str) -> str:
    """
    Initiate a new transaction between two accounts after balance validation.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/transactions/create",
            json={
                "account_number": from_account,
                "to_account_number": to_account,
                "amount": amount
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 201:
            return f"Transaction successful: {response.json()}"
        return f"Transaction failed: {response.text}"

@tool
async def get_transaction_tool(transaction_id: str, token: str) -> str:
    """
    Fetch details of a specific transaction.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/transactions/{transaction_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return f"Transaction details: {response.json()}"
        return f"Failed to fetch transaction: {response.text}"

@tool
async def list_transactions_by_account_tool(account_number: str, token: str) -> str:
    """
    Fetch all transactions for a given account.
    """


    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/transactions/account/{account_number}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            transactions = response.json()
            return f"Transaction history for account {account_number}:\n{transactions}"
        return f"Failed to fetch transactions: {response.text}"
    

