from langsmith import Client
import os

client = Client(api_key = os.getenv("LANGSMITH_API_KEY"),api_url=os.getenv("LANGSMITH_ENDPOINT"))