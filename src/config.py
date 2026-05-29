import json
import os
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv


class TelegramConfig(BaseModel):
    api_id: int
    api_hash: str
    phone: str
    session_name: str = "translator_bot"
    source_channel: str
    target_channel: str
    # Параметры клиента для Telegram
    device_model: str = "Desktop"
    system_version: str = "Windows 10"
    app_version: str = "4.8.1 x64"
    lang_code: str = "en"
    system_lang_code: str = "en-US"


class GeminiConfig(BaseModel):
    api_keys: List[str]
    model: str = "gemini-3.5-flash"
    max_retries: int = 3


class FilterConfig(BaseModel):
    spam_keywords: List[str] = Field(default_factory=list)
    allowed_domains: List[str] = Field(default_factory=lambda: ["t.me"])
    remove_referral_params: bool = True
    handle_reposts: str = "summarize"  # "remove" or "summarize"


class ProcessingConfig(BaseModel):
    check_interval: int = 60
    batch_size: int = 10
    realtime: bool = False  # Режим реального времени через события


class AlertConfig(BaseModel):
    enabled: bool = False
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None


class Config(BaseModel):
    telegram: TelegramConfig
    gemini: GeminiConfig
    filters: FilterConfig
    processing: ProcessingConfig
    alerts: AlertConfig = Field(default_factory=AlertConfig)

    @classmethod
    def load(cls, path: str = "config.json") -> "Config":
        """
        Загрузить конфигурацию из JSON файла или переменных окружения
        
        Приоритет: переменные окружения > config.json
        """
        # Загрузить .env если существует
        load_dotenv()
        
        # Попытаться загрузить из JSON
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}
        
        # Переопределить из переменных окружения если они есть
        telegram_api_id = os.getenv("TELEGRAM_API_ID")
        if telegram_api_id:
            if "telegram" not in data:
                data["telegram"] = {}
            data["telegram"]["api_id"] = int(telegram_api_id)
            
            telegram_api_hash = os.getenv("TELEGRAM_API_HASH")
            if telegram_api_hash:
                data["telegram"]["api_hash"] = telegram_api_hash
            
            telegram_phone = os.getenv("TELEGRAM_PHONE")
            if telegram_phone:
                data["telegram"]["phone"] = telegram_phone
            
            source_channel = os.getenv("SOURCE_CHANNEL")
            if source_channel:
                data["telegram"]["source_channel"] = source_channel
            
            target_channel = os.getenv("TARGET_CHANNEL")
            if target_channel:
                data["telegram"]["target_channel"] = target_channel
        
        gemini_keys = os.getenv("GEMINI_API_KEYS")
        if gemini_keys:
            if "gemini" not in data:
                data["gemini"] = {}
            keys = gemini_keys.split(",")
            data["gemini"]["api_keys"] = [k.strip() for k in keys]
        
        return cls(**data)
