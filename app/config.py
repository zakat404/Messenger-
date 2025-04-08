import os

class Settings:

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://ser:mysecretpassword@db:5432/default_db"
    )
    JWT_SECRET: str = os.getenv("JWT_SECRET", "SUPER_SECRET_JWT_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()
