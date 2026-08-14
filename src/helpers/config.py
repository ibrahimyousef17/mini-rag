from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str
    app_version: str
    file_max_size : int 
    file_allowd_extention : list
    file_defult_chunk_size : int 
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
def get_settings():
    return Settings()