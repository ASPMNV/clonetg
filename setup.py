#!/usr/bin/env python3
"""
Скрипт для первоначальной настройки бота
"""

import json
import os
from pathlib import Path


def create_config():
    """Создать конфигурационный файл"""
    print("=" * 60)
    print("Настройка Telegram Channel Translator Bot")
    print("=" * 60)
    print()
    
    # Telegram настройки
    print("📱 Telegram API настройки")
    print("Получите API credentials на https://my.telegram.org/apps")
    api_id = input("API ID: ").strip()
    api_hash = input("API Hash: ").strip()
    phone = input("Номер телефона (с кодом страны, например +79991234567): ").strip()
    
    print()
    print("📡 Каналы")
    source_channel = input("Канал-источник (например @channel или -100123456789): ").strip()
    target_channel = input("Целевой канал (например @mychannel или -100123456789): ").strip()
    
    # Gemini настройки
    print()
    print("🤖 Gemini API настройки")
    print("Получите API ключи на https://makersuite.google.com/app/apikey")
    api_keys_input = input("API ключи (через запятую): ").strip()
    api_keys = [key.strip() for key in api_keys_input.split(",")]
    
    # Фильтры
    print()
    print("🔍 Настройки фильтрации")
    spam_keywords_input = input("Ключевые слова спама (через запятую, по умолчанию: реклама,промокод,скидка): ").strip()
    if spam_keywords_input:
        spam_keywords = [kw.strip() for kw in spam_keywords_input.split(",")]
    else:
        spam_keywords = ["реклама", "промокод", "скидка", "акция", "купон"]
    
    handle_reposts = input("Как обрабатывать репосты? (summarize/remove, по умолчанию summarize): ").strip() or "summarize"
    
    # Создать конфигурацию
    config = {
        "telegram": {
            "api_id": int(api_id),
            "api_hash": api_hash,
            "phone": phone,
            "session_name": "translator_bot",
            "source_channel": source_channel,
            "target_channel": target_channel
        },
        "gemini": {
            "api_keys": api_keys,
            "model": "gemini-3.5-flash",
            "max_retries": 3
        },
        "filters": {
            "spam_keywords": spam_keywords,
            "allowed_domains": ["t.me"],
            "remove_referral_params": True,
            "handle_reposts": handle_reposts
        },
        "processing": {
            "check_interval": 60,
            "batch_size": 10
        }
    }
    
    # Сохранить конфигурацию
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print()
    print("✅ Конфигурация сохранена в config.json")
    print()
    print("Следующие шаги:")
    print("1. Установите зависимости: pip install -r requirements.txt")
    print("2. Запустите бота: python main.py")
    print("3. При первом запуске введите код подтверждения из Telegram")


def create_directories():
    """Создать необходимые директории"""
    directories = ["data", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Директории созданы")


if __name__ == "__main__":
    try:
        create_directories()
        create_config()
    except KeyboardInterrupt:
        print("\n\n❌ Настройка отменена")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
