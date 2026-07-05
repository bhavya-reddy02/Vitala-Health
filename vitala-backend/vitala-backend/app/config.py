"""Application settings, read from environment variables (or a .env file)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # PostgreSQL connection (user / health data)
    database_url: str = "postgresql+psycopg2://vitala:vitala_pw@localhost:5432/vitala"
    # Redis connection (sessions / leaderboard)
    redis_url: str = "redis://localhost:6379/0"

    # JWT auth
    jwt_secret: str = "dev-secret-change-me"
    jwt_expire_minutes: int = 10080  # 7 days

    # Phase 2 — LLM assistant + RAG
    llm_provider: str = "huggingface"                   # "huggingface" (default) | "anthropic" | "gemini" | "ollama"
    # Anthropic (Claude) — used when llm_provider="anthropic"
    anthropic_api_key: str = ""
    chat_model: str = "claude-3-5-sonnet-20241022"
    # Google Gemini — used when llm_provider="gemini"
    google_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"
    # Ollama (local) — used when llm_provider="ollama"
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3.2"
    # Hugging Face — used when llm_provider="huggingface"
    huggingfacehub_api_token: str = ""
    huggingface_model: str = "Qwen/Qwen2.5-72B-Instruct"
    # RAG
    chroma_dir: str = "/data/chroma"                  # where the vector index is persisted
    embed_model: str = "BAAI/bge-small-en-v1.5"       # local fastembed model

    def llm_ready(self) -> bool:
        """Ollama needs no key; Gemini, Anthropic and Hugging Face each need their own."""
        if self.llm_provider == "ollama":
            return True
        if self.llm_provider == "gemini":
            return bool(self.google_api_key)
        if self.llm_provider == "huggingface":
            return bool(self.huggingfacehub_api_token)
        return bool(self.anthropic_api_key)

    # Comma-separated list of allowed frontend origins
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
