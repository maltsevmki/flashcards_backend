from pydantic_settings import BaseSettings


isDev = True
if isDev:
    from dotenv import load_dotenv
    load_dotenv()


# class MCPSettings(BaseSettings):
#     host: str = '0.0.0.0'
#     port: int = 8000
# class LLMSettings(BaseSettings):
#     openai_api_key: str

#     class Config:
#         env_prefix = 'LLM_'


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
    # llm: LLMSettings = LLMSettings()
    # mcp: MCPSettings = MCPSettings()

    class Config:
        env_file = '.env'


settings = Settings()
