# Telegram Channel Translator

Автоматический перевод постов из Telegram канала на тайский язык через Gemini 3.5 Flash.

## Быстрый старт

```bash
# 1. Установка
pip install -r requirements.txt

# 2. Настройка
copy config.example.json config.json
# Заполните api_id, api_hash, phone, каналы, gemini ключи

# 3. Запуск
python main.py
# При первом запуске введите код из Telegram
```

## Конфигурация

```json
{
  "telegram": {
    "api_id": 12345678,              // https://my.telegram.org/apps
    "api_hash": "your_hash",
    "phone": "+79991234567",
    "source_channel": "@source",
    "target_channel": "@target"
  },
  "gemini": {
    "api_keys": ["key1", "key2"]     // https://makersuite.google.com/app/apikey
  }
}
```

## Возможности

- Парсинг через Telethon
- Перевод через Gemini 3.5 Flash с ротацией ключей
- Автоматическая авторизация (файл сессии)
- Фильтрация спама и реферальных ссылок
- Обработка репостов (удаление или резюме)
- Сохранение медиа (фото, видео)

## Утилиты

```bash
python utils/check_channels.py    # Проверка доступа к каналам
python utils/test_translation.py  # Тест перевода
```

## Docker

```bash
docker-compose up -d
```

## Systemd (Linux)

```bash
sudo bash scripts/install_service.sh
```

## Документация

- [START.md](START.md) - запуск за 1 минуту
- [INSTALL.md](INSTALL.md) - подробная установка
- [USAGE.md](USAGE.md) - настройка фильтров
- [SESSION_GUIDE.md](SESSION_GUIDE.md) - работа с сессиями
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - решение проблем
- [ARCHITECTURE.md](ARCHITECTURE.md) - архитектура

## Лицензия

MIT
