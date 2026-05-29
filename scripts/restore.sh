#!/bin/bash
# Скрипт для восстановления из резервной копии

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Восстановление из резервной копии ===${NC}"
echo

# Получить текущую директорию
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_DIR}/backups"

# Проверить наличие бэкапов
if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A $BACKUP_DIR/*.tar.gz 2>/dev/null)" ]; then
    echo -e "${RED}Ошибка: Резервные копии не найдены${NC}"
    exit 1
fi

# Показать список бэкапов
echo -e "${YELLOW}Доступные резервные копии:${NC}"
ls -lh "$BACKUP_DIR"/*.tar.gz
echo

# Получить последний бэкап
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/*.tar.gz | head -1)
echo -e "${YELLOW}Последняя резервная копия: $(basename $LATEST_BACKUP)${NC}"

# Подтверждение
read -p "Восстановить из этой копии? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Отменено${NC}"
    exit 0
fi

# Создать временную директорию
TEMP_DIR=$(mktemp -d)
echo -e "${YELLOW}Распаковка в ${TEMP_DIR}...${NC}"

# Распаковать
tar -xzf "$LATEST_BACKUP" -C "$TEMP_DIR"

# Восстановить файлы
echo -e "${YELLOW}Восстановление файлов...${NC}"

# Конфигурация
if [ -f "${TEMP_DIR}/config.json" ]; then
    cp "${TEMP_DIR}/config.json" "${PROJECT_DIR}/config.json"
    echo -e "${GREEN}✓ config.json восстановлен${NC}"
fi

# Сессия
if [ -f "${TEMP_DIR}"/*.session ]; then
    cp "${TEMP_DIR}"/*.session "${PROJECT_DIR}/"
    echo -e "${GREEN}✓ Сессия восстановлена${NC}"
fi

# Журнал сессии (если есть)
if [ -f "${TEMP_DIR}"/*.session-journal ]; then
    cp "${TEMP_DIR}"/*.session-journal "${PROJECT_DIR}/"
    echo -e "${GREEN}✓ Журнал сессии восстановлен${NC}"
fi

# База данных
if [ -d "${TEMP_DIR}/data" ]; then
    cp -r "${TEMP_DIR}/data" "${PROJECT_DIR}/"
    echo -e "${GREEN}✓ База данных восстановлена${NC}"
fi

# Очистить временную директорию
rm -rf "$TEMP_DIR"

echo
echo -e "${GREEN}=== Восстановление завершено! ===${NC}"
echo -e "${YELLOW}Перезапустите бота для применения изменений${NC}"
