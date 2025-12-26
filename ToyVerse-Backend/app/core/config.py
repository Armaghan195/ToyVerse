
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):

    db_server: str = Field(default="ZOHAD\\SQLEXPRESS", alias="DB_SERVER")
    db_name: str = Field(default="ToyVerseDB", alias="DB_NAME")
    db_driver: str = Field(default="ODBC Driver 17 for SQL Server", alias="DB_DRIVER")

    secret_key: str = Field(default="your-secret-key-change-in-production", alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")

    smtp_server: str = Field(default="smtp.gmail.com", alias="SMTP_SERVER")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: str = Field(default="", alias="SMTP_USERNAME")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")

    app_name: str = Field(default="ToyVerse API", alias="APP_NAME")
    debug: bool = Field(default=True, alias="DEBUG")
    api_v1_prefix: str = Field(default="/api", alias="API_V1_PREFIX")

    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5500",
            "http://127.0.0.1:5500",
            "http://localhost:8000",
            "http://localhost:5173"
        ],
        alias="CORS_ORIGINS"
    )

    class Config:

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def database_url(self) -> str:

        from urllib.parse import quote_plus

        connection_string = (
            f"DRIVER={{{self.db_driver}}};"
            f"SERVER={self.db_server};"
            f"DATABASE={self.db_name};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate=yes"
        )

        connection_url = f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}"
        return connection_url

    @property
    def is_development(self) -> bool:

        return self.debug

settings = Settings()
