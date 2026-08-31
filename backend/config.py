"""Backend configuration loading and startup validation."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    tavily_api_key: str
    supabase_url: str
    supabase_publishable_key: str
    frontend_origins: tuple[str, ...]


def load_settings() -> Settings:
    """Load required settings or fail with an actionable startup error."""
    required_variables = (
        "GROQ_API_KEY",
        "TAVILY_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_PUBLISHABLE_KEY",
    )
    missing = [name for name in required_variables if not os.getenv(name, "").strip()]

    if missing:
        names = ", ".join(missing)
        raise RuntimeError(
            f"Missing required environment variables: {names}. "
            "Copy backend/.env.example to backend/.env and provide values."
        )

    origins = tuple(
        origin.strip().rstrip("/")
        for origin in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    )

    return Settings(
        groq_api_key=os.environ["GROQ_API_KEY"],
        tavily_api_key=os.environ["TAVILY_API_KEY"],
        supabase_url=os.environ["SUPABASE_URL"].rstrip("/"),
        supabase_publishable_key=os.environ["SUPABASE_PUBLISHABLE_KEY"],
        frontend_origins=origins,
    )


settings = load_settings()
