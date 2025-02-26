from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str
    OPENAI_API_KEY: str
    DB_HOST : str
    DB_PORT : int
    DB_NAME : str
    DB_USER : str
    DB_PASSWORD : str
    PROXY_URL: str
    ASSISTANT_ID: str

    class Config:
        env_file = ".env"

settings = Settings()
