from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    perplexity_api_key: str | None = None
    brave_api_key: str | None = None
    tavily_api_key: str | None = None
    exa_api_key: str | None = None

    # Model used to synthesize answers for retrieval-only providers (Brave/Tavily/Exa).
    retrieval_synthesis_model: str = "gemini-3-pro-preview"

    database_url: str = "sqlite:///./grounding.db"
    cors_origins: str = "http://localhost:3000"
    request_timeout_s: int = 30

    # LLM-as-judge: "google" or "anthropic".
    judge_provider: str = "google"
    judge_model_google: str = "gemini-3-pro-preview"
    judge_model_anthropic: str = "claude-sonnet-4-6"


@lru_cache
def get_settings() -> Settings:
    return Settings()


PROVIDERS = [
    "gemini",
    "claude",
    "openai_ws",
    "perplexity",
    "brave",
    "tavily",
    "exa",
]
