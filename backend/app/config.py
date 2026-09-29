import os
from typing import Dict, List, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    APP_ENV: str = "development"
    API_PREFIX: str = ""
    DATABASE_URL: str = "sqlite:///./opportunityos.db"
    JWT_SECRET: str = "opportunityos-super-secret-jwt-key-2026-hackathon-secure-32bytes"
    JWT_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # SerpApi
    SERPAPI_API_KEY: str = ""
    SERPAPI_TIMEOUT_SECONDS: int = 20
    SERP_CACHE_TTL_HOURS: int = 12
    SERP_DAILY_BUDGET: int = 80
    ENABLE_YOUTUBE: bool = False

    # LLM Settings
    LLM_PROVIDER: str = "mock"
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_API_KEY: str = ""
    LLM_TEMPERATURE: float = 0.2

    # Agent
    AGENT_MAX_QUERIES: int = 6
    AGENT_TIMEOUT_SECONDS: int = 60
    GAP_TOP_N: int = 15
    LOG_LEVEL: str = "INFO"
    LOG_LLM_PROMPTS: bool = False

    # Match weights as per TRD
    MATCH_WEIGHTS: Dict[str, float] = Field(
        default_factory=lambda: {
            "skills": 0.50,
            "role": 0.15,
            "location": 0.15,
            "experience": 0.10,
            "type": 0.10,
        }
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        return ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
