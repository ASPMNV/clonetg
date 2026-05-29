#!/bin/bash
# Скрипт для удаления systemd сервиса

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Удаление Telegram Channel Translator сервиса ===${NC}"
echo

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Ошибка: Запустите скрипт с sudo${NC}"
    exit 1
fi

SERVICE_FILE="/etc/systemd/system/telegram-translator.service"

# Остановить сервис
echo -e "${GREEN}Остановка сервиса...${NC}"
systemctl stop telegram-translator 2>/dev/null || true

# Отключить автозапуск
echo -e "${GREEN}Отключение автозапуска...${NC}"
systemctl disable telegram-translator 2>/dev/null || true

# Удалить файл сервиса
if [ -f "$SERVICE_FILE" ]; then
    echo -e "${GREEN}Удаление файла сервиса...${NC}"
    rm "$SERVICE_FILE"
    echo -e "${GREEN}✓ Файл сервиса удален${NC}"
else
    echo -e "${YELLOW}Файл сервиса не найден${NC}"
fi

# Перезагрузить systemd
echo -e "${GREEN}Перезагрузка systemd...${NC}"
systemctl daemon-reload

echo
echo -e "${GREEN}=== Удаление завершено! ===${NC}"
