from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str
    app_version: str
    file_max_size: int 
    file_allowd_extention: list
    file_defult_chunk_size: int 
    mongodb_url: str
    mongodb_name: str
    
    MONGO_USER: str | None = None
    MONGO_PASS: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"  
    )

def get_settings():
    return Settings() # type: ignore