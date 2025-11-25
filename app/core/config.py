from pydantic_settings import BaseSettings


isDev = False
if isDev:
    from dotenv import load_dotenv
    load_dotenv()


class AppSettings(BaseSettings):
    title: str
    description: str
    version: str

    class Config:
        env_prefix = 'APP_'


class SecuritySettings(BaseSettings):
    secret_token: str

    class Config:
        env_prefix = 'SECURITY_'


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    security: SecuritySettings = SecuritySettings()

    class Config:
        env_file = '.env'


settings = Settings()
