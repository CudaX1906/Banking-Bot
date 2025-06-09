from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Config(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    NVIDIA_API_KEY: str = Field(..., env="NVIDIA_API_KEY")
    LANGSMITH_API_KEY: str = Field(..., env="LANGSMITH_API_KEY")
    LANGSMITH_TRACING: str = Field("true", env="LANGSMITH_TRACING")
    LANGSMITH_ENDPOINT: str = Field("https://api.smith.langchain.com", env="LANGSMITH_ENDPOINT")
    LANGSMITH_PROJECT: str = Field("bank-bot", env="LANGSMITH_PROJECT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    API_BASE_URL: str = Field("http://localhost:8000", env="API_BASE_URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

config = Config()
