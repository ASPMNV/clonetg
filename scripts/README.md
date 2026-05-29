# Скрипты для управления ботом

Эта директория содержит полезные скрипты для управления ботом.

## Доступные скрипты

### install_service.sh (Linux)

Устанавливает бота как systemd сервис для автоматического запуска.

**Использование:**
```bash
sudo bash scripts/install_service.sh
```

**Что делает:**
- Создает systemd unit файл
- Настраивает автозапуск при загрузке системы
- Настраивает автоматический перезапуск при сбоях

**После установки:**
```bash
# Запустить
sudo systemctl start telegram-translator

# Остановить
sudo systemctl stop telegram-translator

# Перезапустить
sudo systemctl restart telegram-translator

# Статус
sudo systemctl status telegram-translator

# Логи
journalctl -u telegram-translator -f
```

### uninstall_service.sh (Linux)

Удаляет systemd сервис.

**Использование:**
```bash
sudo bash scripts/uninstall_service.sh
```

### backup.sh

Создает резервную копию важных файлов.

**Использование:**
```bash
bash scripts/backup.sh
```

**Что сохраняется:**
- config.json
- *.session (сессия Telegram)
- data/ (база данных)

**Где хранится:**
- Директория `backups/` в корне проекта
- Автоматически удаляются копии старше 30 дней

### restore.sh

Восстанавливает из резервной копии.

**Использование:**
```bash
bash scripts/restore.sh
```

**Что делает:**
- Показывает список доступных бэкапов
- Восстанавливает файлы из выбранного бэкапа
- Сохраняет текущие файлы перед восстановлением

## Примеры использования

### Установка как сервис

```bash
# 1. Установить сервис
sudo bash scripts/install_service.sh

# 2. Запустить
sudo systemctl start telegram-translator

# 3. Проверить статус
sudo systemctl status telegram-translator
```

### Регулярное резервное копирование

Добавьте в crontab для ежедневного бэкапа:

```bash
# Открыть crontab
crontab -e

# Добавить строку (бэкап каждый день в 3:00)
0 3 * * * cd /path/to/telegram-channel-translator && bash scripts/backup.sh
```

### Восстановление после сбоя

```bash
# 1. Остановить бота
sudo systemctl stop telegram-translator

# 2. Восстановить из бэкапа
bash scripts/restore.sh

# 3. Запустить снова
sudo systemctl start telegram-translator
```

## Требования

- **Linux** для systemd скриптов
- **bash** для всех скриптов
- **sudo** права для install/uninstall скриптов
- **tar** для backup/restore скриптов

## Безопасность

⚠️ **Важно:**
- Резервные копии содержат конфиденциальные данные
- Храните бэкапы в безопасном месте
- Не публикуйте бэкапы в публичных репозиториях
- Регулярно проверяйте возможность восстановления

## Автоматизация

### Пример: Полная автоматизация

```bash
#!/bin/bash
# auto-maintain.sh - Автоматическое обслуживание

# Создать бэкап
bash scripts/backup.sh

# Проверить статус
if ! systemctl is-active --quiet telegram-translator; then
    echo "Бот не запущен, перезапуск..."
    sudo systemctl restart telegram-translator
fi

# Очистить старые логи (старше 7 дней)
find logs/ -name "*.log" -mtime +7 -delete

# Оптимизировать базу данных
sqlite3 data/posts.db "VACUUM;"

echo "Обслуживание завершено"
```

Добавьте в crontab:
```bash
0 4 * * * cd /path/to/telegram-channel-translator && bash auto-maintain.sh
```

## Мониторинг

### Проверка работы сервиса

```bash
#!/bin/bash
# check-health.sh

if systemctl is-active --quiet telegram-translator; then
    echo "✓ Сервис работает"
else
    echo "✗ Сервис не работает"
    exit 1
fi

# Проверить последние ошибки
ERROR_COUNT=$(journalctl -u telegram-translator --since "1 hour ago" | grep -c "ERROR")

if [ $ERROR_COUNT -gt 10 ]; then
    echo "⚠ Обнаружено $ERROR_COUNT ошибок за последний час"
    exit 1
fi

echo "✓ Все в порядке"
```

## Troubleshooting

### Сервис не запускается

```bash
# Проверить логи
journalctl -u telegram-translator -n 50

# Проверить конфигурацию
systemctl status telegram-translator

# Проверить права
ls -la /etc/systemd/system/telegram-translator.service
```

### Бэкап не создается

```bash
# Проверить права на директорию
ls -la backups/

# Создать директорию вручную
mkdir -p backups
chmod 755 backups
```

### Восстановление не работает

```bash
# Проверить содержимое бэкапа
tar -tzf backups/backup_YYYYMMDD_HHMMSS.tar.gz

# Распаковать вручную
tar -xzf backups/backup_YYYYMMDD_HHMMSS.tar.gz -C /tmp/restore
```
