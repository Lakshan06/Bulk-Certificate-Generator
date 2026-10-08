from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    database_url: str = "sqlite:///./certificates.db"
    output_dir: Path = Path("./generated_certificates")
    max_recipients_per_job: int = 1000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

# Ensure output directory exists
settings.output_dir.mkdir(parents=True, exist_ok=True)
