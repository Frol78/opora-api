# Импортируем BaseSettings и SettingsConfigDict из библиотеки pydantic-settings.
# Эта библиотека создана специально для безопасного чтения настроек из .env файлов.
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Указываем настройки нашего приложения с типами и значениями по умолчанию.
    # Если переменная не найдется в .env, FastAPI возьмет значение по умолчанию.
    app_name: str = "Опора API"
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 60
    debug: bool = False

    # Указываем Pydantic, откуда брать значения — из файла .env в корне проекта.
    # extra="ignore" говорит Pydantic не падать, если в .env окажутся лишние переменные.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Создаем единственный глобальный экземпляр настроек.
# Теперь мы сможем импортировать `settings` в любой файл нашего проекта 
# и безопасно доставать оттуда параметры (например, settings.database_url).
settings = Settings()