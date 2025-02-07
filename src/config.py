import os
from pydantic_settings import SettingsConfigDict, BaseSettings
from dotenv import load_dotenv

__all__ = ['Settings', 'settings']

load_dotenv()

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    )

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"  
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    SECRET_KEY = os.environ.get("SECRET_KEY", default="SECRET_KEY")
    ALGORITHM = os.environ.get("ALGORITHM", default="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", default=180))

settings = Settings()



