import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str
    OPENAI_API_KEY: str
    PROXY_URL: str
    ASSISTANT_ID: str
    TEMP_DIR: str

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int
    POSTGRES_HOST: str

    DOCKER_MODE: str

    #Чтобы не менять каждый раз локалхост на дб
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.POSTGRES_HOST = os.getenv("POSTGRES_HOST") if self.DOCKER_MODE.lower() == "true" else "localhost"

    @property
    def DATABASE_URL(self) -> str:
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    class Config:
        env_file = "../../.env"

settings = Settings()
