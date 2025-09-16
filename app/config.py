import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/api_ad"
    )
    
    api_title: str = "factory-class-crud-generator"
    api_description: str = "Auto-generated CRUD API from model classes"
    api_version: str = "1.0.0"
    
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    models_dir: str = "models"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

