# Руководство по использованию

## Основные команды

### Запуск бота

```bash
python main.py
```

### Проверка настроек

```bash
# Проверить доступ к каналам
python utils/check_channels.py

# Протестировать перевод
python utils/test_translation.py
```

### Первоначальная настройка

```bash
python setup.py
```

## Как работает бот

1. **Авторизация в Telegram**
   - При первом запуске запрашивается код из Telegram
   - Сессия сохраняется в файл `translator_bot.session`
   - При следующих запусках используется сохраненная сессия

2. **Мониторинг канала-источника**
   - Бот проверяет новые посты каждые N секунд (настраивается в `config.json`)
   - Использует Telethon для получения сообщений

3. **Фильтрация контента**
   - Проверка на спам по ключевым словам
   - Фильтрация реферальных ссылок
   - Обработка репостов (удаление или резюме)

4. **Перевод**
   - Текст переводится на тайский через Gemini API
   - Автоматическая ротация API ключей
   - Сохранение форматирования и эмодзи

5. **Публикация**
   - Пост публикуется в целевой канал
   - Сохраняется структура (фото, видео, форматирование)
   - Информация о обработке сохраняется в БД

### Настройка клиента Telegram

Бот использует параметры клиента для идентификации в Telegram:

```json
"telegram": {
  "device_model": "Desktop",
  "system_version": "Windows 10",
  "app_version": "4.8.1 x64",
  "lang_code": "en",
  "system_lang_code": "en-US"
}
```

**Зачем это нужно:**
- Telegram видит ваше устройство в списке активных сессий
- Помогает избежать блокировок
- Делает сессию более "легитимной"

**Можно изменить на:**
- `device_model`: "iPhone 12", "Samsung Galaxy", "MacBook Pro"
- `system_version`: "iOS 15", "Android 12", "macOS 12"
- `app_version`: версия Telegram клиента

## Настройка фильтров

### Фильтрация спама

Бот считает пост спамом если:
- Найдено 2+ ключевых слова из списка `spam_keywords`
- Более 3 ссылок в посте
- Более 30% текста составляют эмодзи

Настройка в `config.json`:

```json
"filters": {
  "spam_keywords": [
    "реклама",
    "промокод",
    "скидка"
  ]
}
```

### Фильтрация ссылок

Бот удаляет:
- Ссылки на домены не из списка `allowed_domains`
- Реферальные параметры (utm_*, ref, affiliate и т.д.)

Настройка:

```json
"filters": {
  "allowed_domains": ["t.me", "example.com"],
  "remove_referral_params": true
}
```

### Обработка репостов

**Режим "summarize"** (рекомендуется):
- Создает краткое резюме содержания репоста
- Резюме переводится на тайский
- Добавляется в начало поста

**Режим "remove"**:
- Полностью удаляет репосты
- Такие посты не публикуются

```json
"filters": {
  "handle_reposts": "summarize"
}
```

## Ротация API ключей

Бот автоматически чередует API ключи Gemini для:
- Обхода лимитов free tier
- Повышения надежности
- Распределения нагрузки

Добавьте несколько ключей в конфигурацию:

```json
"gemini": {
  "api_keys": [
    "key_from_account_1",
    "key_from_account_2",
    "key_from_account_3"
  ]
}
```

Бот выбирает наименее используемый ключ за последний час.

## Работа с медиа

Бот поддерживает:
- ✅ Фотографии
- ✅ Видео
- ✅ Документы
- ✅ GIF анимации
- ✅ Спойлеры на медиа

Медиа автоматически скачивается и загружается в целевой канал.

## База данных

Бот использует SQLite для хранения:
- Обработанных постов (избежание дубликатов)
- Статистики использования API ключей
- Ошибок обработки

База находится в `data/posts.db`.

### Просмотр базы данных

```bash
sqlite3 data/posts.db

# Посмотреть обработанные посты
SELECT * FROM processed_posts ORDER BY processed_at DESC LIMIT 10;

# Статистика по API ключам
SELECT api_key_index, COUNT(*) as usage_count 
FROM api_key_usage 
WHERE used_at > datetime('now', '-1 hour')
GROUP BY api_key_index;
```

## Логирование

Логи сохраняются в:
- `logs/bot.log` - полный лог работы
- Консоль - важные события

Уровни логирования:
- INFO - обычная работа
- WARNING - предупреждения
- ERROR - ошибки

## Мониторинг работы

### Проверка статуса

```bash
# Посмотреть последние логи
tail -f logs/bot.log

# Проверить процесс
ps aux | grep main.py
```

### Статистика

```bash
# Количество обработанных постов
sqlite3 data/posts.db "SELECT COUNT(*) FROM processed_posts WHERE status='success';"

# Количество отфильтрованных
sqlite3 data/posts.db "SELECT COUNT(*) FROM processed_posts WHERE status='filtered';"

# Ошибки
sqlite3 data/posts.db "SELECT * FROM processed_posts WHERE status='error';"
```

## Частые сценарии

### Добавление нового API ключа

1. Откройте `config.json`
2. Добавьте ключ в массив `gemini.api_keys`
3. Перезапустите бота

### Изменение интервала проверки

```json
"processing": {
  "check_interval": 30  // секунды
}
```

### Изменение размера пакета

```json
"processing": {
  "batch_size": 20  // количество постов за раз
}
```

### Очистка базы данных

```bash
# Удалить старые записи (старше 30 дней)
sqlite3 data/posts.db "DELETE FROM processed_posts WHERE processed_at < datetime('now', '-30 days');"

# Полная очистка (начать заново)
rm data/posts.db
```

## Остановка бота

### Graceful shutdown

Нажмите `Ctrl+C` в консоли. Бот корректно завершит работу.

### Принудительная остановка

```bash
# Linux/macOS
pkill -f main.py

# Windows
taskkill /F /IM python.exe
```

## Docker

### Сборка

```bash
docker-compose build
```

### Запуск

```bash
docker-compose up -d
```

### Логи

```bash
docker-compose logs -f
```

### Остановка

```bash
docker-compose down
```

## Резервное копирование

Важные файлы для бэкапа:
- `config.json` - конфигурация
- `translator_bot.session` - сессия Telegram (важно!)
- `translator_bot.session-journal` - журнал сессии (если есть)
- `data/posts.db` - база данных

```bash
# Создать бэкап
tar -czf backup_$(date +%Y%m%d).tar.gz config.json *.session* data/

# Восстановить
tar -xzf backup_20240101.tar.gz
```

### Важно о файле сессии

**Что это:**
- Файл `translator_bot.session` содержит вашу авторизацию в Telegram
- Позволяет боту работать без повторного ввода кода

**Безопасность:**
- ⚠️ Храните файл в безопасности
- ⚠️ Не публикуйте в Git
- ⚠️ С этим файлом можно получить доступ к вашему Telegram

**Перенос на другой сервер:**
```bash
# Включите файл сессии в бэкап
tar -czf backup.tar.gz config.json *.session* data/

# На новом сервере
tar -xzf backup.tar.gz
python main.py  # Запустится без запроса кода
```

## Безопасность

⚠️ **Важно:**
- Не публикуйте `config.json` в публичных репозиториях
- Храните API ключи в безопасности
- Регулярно меняйте пароли
- Используйте двухфакторную аутентификацию в Telegram

## Производительность

Рекомендации:
- Используйте 3-5 API ключей Gemini
- Интервал проверки: 30-60 секунд
- Размер пакета: 10-20 постов
- Регулярно очищайте старые записи из БД
