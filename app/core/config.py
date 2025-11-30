from pydantic_settings import BaseSettings


isDev = True
if isDev:
    from dotenv import load_dotenv
    load_dotenv()


class AppSettings(BaseSettings):
    title: str
    description: str
    version: str

    class Config:
        env_prefix = 'APP_'


class DatabaseSettings(BaseSettings):
    url: str

    class Config:
        env_prefix = 'DB_'


class SecuritySettings(BaseSettings):
    secret_token: str

    class Config:
        env_prefix = 'SECURITY_'


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    security: SecuritySettings = SecuritySettings()
    db: DatabaseSettings = DatabaseSettings()

    class Config:
        env_file = '.env'


settings = Settings()
