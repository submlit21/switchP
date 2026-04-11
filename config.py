from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Network device console management settings."""

    port: str = Field(default="/dev/ttyUSB0", description="Serial port path")
    baud_rate: int = Field(default=9600, description="Serial baud rate")


config = Settings()
