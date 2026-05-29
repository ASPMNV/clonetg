# Инструкция по установке и настройке

## Требования

- Python 3.8 или выше
- Telegram аккаунт
- Gemini API ключи (бесплатные)

## Шаг 1: Установка зависимостей

```bash
pip install -r requirements.txt
```

## Шаг 2: Получение Telegram API credentials

1. Перейдите на https://my.telegram.org/apps
2. Войдите в свой аккаунт Telegram
3. Создайте новое приложение
4. Сохраните `api_id` и `api_hash`

## Шаг 3: Получение Gemini API ключей

1. Перейдите на https://makersuite.google.com/app/apikey
2. Войдите в Google аккаунт
3. Создайте новый API ключ
4. Повторите для нескольких аккаунтов (для ротации)

## Шаг 4: Настройка каналов

### Канал-источник
- Вы должны быть подписаны на канал
- Получите username канала (например `@channelname`) или ID

### Целевой канал
- Вы должны быть администратором канала
- Получите username канала или ID
- Убедитесь, что у вас есть права на публикацию

## Шаг 5: Конфигурация

### Автоматическая настройка (рекомендуется)

```bash
python setup.py
```

Следуйте инструкциям на экране.

### Ручная настройка

1. Скопируйте `config.example.json` в `config.json`:
```bash
cp config.example.json config.json
```

2. Отредактируйте `config.json`:

```json
{
  "telegram": {
    "api_id": 12345678,
    "api_hash": "your_api_hash_here",
    "phone": "+79991234567",
    "session_name": "translator_bot",
    "source_channel": "@source_channel",
    "target_channel": "@target_channel"
  },
  "gemini": {
    "api_keys": [
      "your_gemini_key_1",
      "your_gemini_key_2",
      "your_gemini_key_3"
    ],
    "model": "gemini-3.5-flash",
    "max_retries": 3
  },
  "filters": {
    "spam_keywords": [
      "реклама",
      "промокод",
      "скидка",
      "акция"
    ],
    "allowed_domains": ["t.me"],
    "remove_referral_params": true,
    "handle_reposts": "summarize"
  },
  "processing": {
    "check_interval": 60,
    "batch_size": 10
  }
}
```

## Шаг 6: Проверка настроек

### Проверка доступа к каналам

```bash
python utils/check_channels.py
```

### Тест перевода

```bash
python utils/test_translation.py
```

## Шаг 7: Первый запуск

```bash
python main.py
```

При первом запуске:
1. Вам будет отправлен код подтверждения в Telegram
2. Введите код в консоль
3. Если у вас включена двухфакторная аутентификация, введите пароль
4. **Сессия будет сохранена в файл `translator_bot.session`**

### Важно о файле сессии

После первой авторизации создается файл `translator_bot.session`:
- ✅ Этот файл содержит вашу авторизацию
- ✅ При следующих запусках код подтверждения не потребуется
- ✅ Храните этот файл в безопасности (он в `.gitignore`)
- ✅ Можно перенести на другой сервер для авторизации без телефона

**Перенос на другой сервер:**
```bash
# Скопируйте файл сессии на новый сервер
scp translator_bot.session user@server:/path/to/bot/

# На новом сервере бот запустится без запроса кода
python main.py
```

## Настройка фильтров

### Ключевые слова спама

Добавьте слова, которые часто встречаются в рекламных постах:

```json
"spam_keywords": [
  "реклама",
  "промокод",
  "скидка",
  "акция",
  "купон",
  "распродажа"
]
```

### Разрешенные домены

Укажите домены, ссылки на которые разрешены:

```json
"allowed_domains": ["t.me", "example.com"]
```

### Обработка репостов

- `"summarize"` - создать краткое резюме репоста на тайском
- `"remove"` - полностью удалить репосты

```json
"handle_reposts": "summarize"
```

## Запуск в фоновом режиме

### Linux/macOS

```bash
nohup python main.py > output.log 2>&1 &
```

### Windows

Используйте Task Scheduler или создайте bat-файл:

```batch
@echo off
python main.py
pause
```

### Docker (опционально)

```bash
docker build -t telegram-translator .
docker run -d --name translator telegram-translator
```

## Мониторинг

Логи сохраняются в директории `logs/`:
- `logs/bot.log` - основной лог

База данных обработанных постов:
- `data/posts.db` - SQLite база данных

## Устранение проблем

### Ошибка авторизации Telegram
- Проверьте правильность `api_id` и `api_hash`
- Убедитесь, что номер телефона указан с кодом страны

### Ошибка доступа к каналу
- Убедитесь, что вы подписаны на канал-источник
- Убедитесь, что вы администратор целевого канала

### Ошибка Gemini API
- Проверьте правильность API ключей
- Убедитесь, что не превышен лимит запросов
- Попробуйте добавить больше ключей для ротации

### Посты не переводятся
- Проверьте логи в `logs/bot.log`
- Убедитесь, что посты не фильтруются как спам
- Проверьте настройки фильтров в `config.json`
