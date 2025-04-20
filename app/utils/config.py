from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str

    SECRET_KEY: str

    # Algorithm used to sign the JWT tokens (default: HS256)
    ALGORITHM: str = "HS256"

    # Token expiration time in minutes (default: 60) You can change it as per the requirement
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # API key for accessing Groq AI services
    GROQ_API_KEY: str

    # Configuration to load variables from a .env file
    class Config:
        env_file = ".env"

settings = Settings()
