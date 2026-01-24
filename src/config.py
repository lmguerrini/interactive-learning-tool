from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings managed via Pydantic and environment variables."""

    # Field(default=...) tells mypy the value is provided by Pydantic's magic
    openai_api_key: str = Field(default=...)
    questions_file: str = "data/questions.json"
    results_file: str = "data/results.txt"

    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.2
    llm_max_completion_tokens: int = 800

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
