import os

from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()
        self.email_sender = os.environ.get("EMAIL_SENDER")
        self.email_password = os.environ.get("EMAIL_PASSWORD")
        self.db_config = DatabaseConfig()
        self.token = Token()


class Token:
    def __init__(self):
        self.secret_key = os.environ.get("SECRET_KEY")
        self.access_token_expire_minute = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
        self.refresh_token_expire_days = os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS")
        self.email_token_expire_minute = os.environ.get("EMAIL_TOKEN_EXPIRE_MINUTES")

class DatabaseConfig:
    def __init__(self):
        self.db_name = os.environ.get("DB_NAME")
        self.db_user = os.environ.get("DB_USER")
        self.db_password = os.environ.get("DB_PASSWORD")
        self.db_host = os.environ.get("DB_HOST")
        self.db_port = os.environ.get("DB_PORT")

    def get_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?async_fallback=true"


config_project = Config()
