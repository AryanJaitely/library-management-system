from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/library_db"
    SECRET_KEY: str = "changethis-at-least-32-characters-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    FINE_PER_DAY: float = 2.0
    DEFAULT_BORROW_DAYS: int = 14

    class Config:
        env_file = ".env"


settings = Settings()
