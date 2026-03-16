from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "offer-matrix-api"
    VERSION: str = "1.0.0"

    # Project paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DATABASE_URL: str = "sqlite:///./offer_matrix.db"

    # AI Config
    ZHIPUAI_API_KEY: str = ""
    AI_MODEL: str = "glm-4"

    # Alibaba Cloud Config
    ALIYUN_ACCESS_KEY: str = ""
    ALIYUN_SECRET_KEY: str = ""
    ALIYUN_APP_ID: str = ""
    ALIYUN_APP_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

    @model_validator(mode="after")
    def set_database_url(self):
        """Point the default SQLite database to the project data directory."""
        if self.DATABASE_URL == "sqlite:///./offer_matrix.db":
            self.DATABASE_URL = f"sqlite:///{self.DATA_DIR}/offer_matrix.db"
        return self


settings = Settings()
