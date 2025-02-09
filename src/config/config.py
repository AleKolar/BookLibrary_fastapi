import os
from pydantic import ValidationError
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

__all__ = ['Settings', 'settings']

load_dotenv()

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    SECRET_KEY: str = os.environ.get("SECRET_KEY", default="SECRET_KEY")
    ALGORITHM: str = os.environ.get("ALGORITHM", default="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", default=180))

    EMAIL_HOST: str = os.environ.get("EMAIL_HOST", default="smtp.yandex.ru")
    EMAIL_PORT: int = int(os.environ.get("EMAIL_PORT", default=465))
    EMAIL_HOST_USER: str = os.environ.get("EMAIL_HOST_USER", default="gefest-173@yandex.ru")
    EMAIL_HOST_PASSWORD: str = os.environ.get("EMAIL_HOST_PASSWORD", default="lppxxgxpqpdqabzw")
    EMAIL_USE_SSL: bool = os.environ.get("EMAIL_USE_SSL", default=True)

    # model_config = SettingsConfigDict(
    #     env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    # )

    class Config:
        env_file = ".env"

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


try:
    settings = Settings()
except ValidationError as e:
    print(f"Validation errors: {e}")
    exit(1)

