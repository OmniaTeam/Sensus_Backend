import os

from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()
        self.secret_key = os.environ.get("SECRET_KEY")
        self.db_config = DatabaseConfig()


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
