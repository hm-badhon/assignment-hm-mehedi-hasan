"""
Configuration module for the application.
"""

import os
from typing import Any, Dict, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration settings loaded from config.yaml and environment variables.
    """

    GEMINI_API_KEY: str = Field(..., validation_alias="GEMINI_API_KEY")

    MODEL_PROVIDER: str = Field(default="")
    MODEL_NAME: str = Field(default="")
    MODEL_TEMPERATURE: float = Field(default=0.7)
    MODEL_TIMEOUT_SECONDS: int = Field(default=60)

    PROCESSING_BATCH_SIZE: int = Field(default=1)
    PROCESSING_RETRY_ATTEMPTS: int = Field(default=3)
    PROCESSING_RETRY_DELAY: int = Field(default=1)

    RATE_LIMIT_MAX_REQUESTS: int = Field(default=100)
    RATE_LIMIT_WINDOW_SECONDS: int = Field(default=3600)

    EMBEDDING_PROVIDER: str = Field(default="")
    EMBEDDING_MODEL: str = Field(default="")

    CHROMA_HOST: str = Field(default="localhost")

    IO_DATA_DIR: str = Field(default="data")
    IO_ENCODING: str = Field(default="utf-8")

    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="logs/log.txt")

    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    DEBUG: bool = Field(default=False)
    WORKERS: int = Field(default=1)

    class Config:
        """Pydantic config for environment variables."""

        env_file = ".env"
        env_file_encoding = "utf-8"


_settings_instance: Optional[Settings] = None


def load_yaml_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to the config.yaml file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If the config file cannot be found
    """
    if not config_path:
        possible_paths = [
            "config.yaml",
            "../config.yaml",
            "config/config.yaml",
            os.path.join(os.path.dirname(__file__), "../../config/config.yaml"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                config_path = path
                break

    if not config_path or not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Configuration file not found. Please ensure config.yaml exists in one of these locations: {', '.join(possible_paths)}"
        )

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_settings() -> Settings:
    """
    Get or create global settings instance with settings from config.yaml.

    Returns:
        Settings instance

    Raises:
        ValueError: If required settings are missing from the config file
        FileNotFoundError: If the config file cannot be found
    """
    global _settings_instance
    if _settings_instance is None:
        try:
            yaml_config = load_yaml_config()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Configuration file not found: {str(e)}")

        _settings_instance = Settings()

        if "model" in yaml_config:
            model_config = yaml_config["model"]
            _settings_instance.MODEL_PROVIDER = model_config.get("provider", "")
            _settings_instance.MODEL_NAME = model_config.get("name", "")
            _settings_instance.MODEL_TEMPERATURE = model_config.get("temperature", 0.7)
            _settings_instance.MODEL_TIMEOUT_SECONDS = model_config.get(
                "timeout_seconds", 60
            )

        if "processing" in yaml_config:
            proc_config = yaml_config["processing"]
            _settings_instance.PROCESSING_BATCH_SIZE = proc_config.get("batch_size", 1)
            _settings_instance.PROCESSING_RETRY_ATTEMPTS = proc_config.get(
                "retry_attempts", 3
            )
            _settings_instance.PROCESSING_RETRY_DELAY = proc_config.get(
                "retry_delay", 1
            )

        if "rate_limit" in yaml_config:
            rl_config = yaml_config["rate_limit"]
            _settings_instance.RATE_LIMIT_MAX_REQUESTS = rl_config.get(
                "max_requests", 100
            )
            _settings_instance.RATE_LIMIT_WINDOW_SECONDS = rl_config.get(
                "window_seconds", 3600
            )

        if "chroma" in yaml_config:
            chroma_config = yaml_config["chroma"]
            _settings_instance.CHROMA_HOST = chroma_config.get("host", "localhost")

        if "embedding" in yaml_config:
            embed_config = yaml_config["embedding"]
            _settings_instance.EMBEDDING_PROVIDER = embed_config.get("provider", "")
            _settings_instance.EMBEDDING_MODEL = embed_config.get("model", "")

        if "io" in yaml_config:
            io_config = yaml_config["io"]
            _settings_instance.IO_DATA_DIR = io_config.get("data_dir", "data")
            _settings_instance.IO_ENCODING = io_config.get("encoding", "utf-8")

        if "logging" in yaml_config:
            log_config = yaml_config["logging"]
            _settings_instance.LOG_LEVEL = log_config.get("level", "INFO")
            _settings_instance.LOG_FILE = log_config.get("file", "logs/log.txt")

        if "server" in yaml_config:
            server_config = yaml_config["server"]
            _settings_instance.HOST = server_config.get("host", "0.0.0.0")
            _settings_instance.PORT = server_config.get("port", 8000)
            _settings_instance.DEBUG = server_config.get("debug", False)
            _settings_instance.WORKERS = server_config.get("workers", 1)

    return _settings_instance
