from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str
    OPENAI_API_KEY: str
    PROXY_URL: str
    ASSISTANT_ID: str
    TEMP_DIR: str = "temp_audio"

    class Config:
        env_file = ".env"

settings = Settings()
