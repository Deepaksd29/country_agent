from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
 
    GEMMINE_API_KEY: str = Field(..., alias="GEMINI_API_KEY")
    MODEL_NAME: str = "gemini-2.5-flash"
    MODEL_TEMPERATURE: float = 0.2
    MODEL_MAX_RETRIES: int = 2
    REST_COUNTRIES_API_URL: str = "https://restcountries.com/v3.1/name"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore" 
    )

# Instantiate the settings
try:
    settings = Settings()
    print("Settings loaded successfully!")
except Exception as e:
    print(f"Configuration Error: {e}")