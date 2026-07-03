import os

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cardio.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production-6f8a2b1c")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    MODEL_PATH: str = os.getenv("MODEL_PATH", "../model/model_results.json")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

settings = Settings()
