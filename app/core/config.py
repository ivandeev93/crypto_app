from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


# Класс настроек для приложения
class Settings(BaseSettings):
    # URL для подключения к базе данных
    DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379/0"
    DERIBIT_BASE_URL: str = "https://www.deribit.com/api"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


# Функция, которая будет возвращать синглтон-экземпляр настроек
@lru_cache()  # Декоратор кэширует результат первого вызова
def get_settings() -> Settings:
    print("Загрузка настроек...")
    return Settings()