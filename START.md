# Запуск за 1 минуту

```bash
# 1. Установка
pip install -r requirements.txt

# 2. Настройка
copy config.example.json config.json
# Отредактируйте config.json (см. ниже)

# 3. Запуск
python main.py
# Введите код из Telegram
```

## Что заполнить в config.json

```json
{
  "telegram": {
    "api_id": 12345678,              // https://my.telegram.org/apps
    "api_hash": "ваш_hash",
    "phone": "+79991234567",
    "source_channel": "@source",
    "target_channel": "@target"
  },
  "gemini": {
    "api_keys": ["ваш_ключ"]         // https://makersuite.google.com/app/apikey
  }
}
```

## Готово! 🚀

При следующем запуске код не нужен.

---

**Подробнее:** [QUICK_START_RU.md](QUICK_START_RU.md)
