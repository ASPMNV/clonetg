#!/bin/bash
# Скрипт для создания резервной копии

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Создание резервной копии ===${NC}"
echo

# Получить текущую директорию
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Имя файла бэкапа
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).tar.gz"
BACKUP_DIR="${PROJECT_DIR}/backups"

# Создать директорию для бэкапов
mkdir -p "$BACKUP_DIR"

echo -e "${YELLOW}Создание архива...${NC}"

# Создать архив
cd "$PROJECT_DIR"
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}" \
    --exclude='backups' \
    --exclude='logs' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='.venv' \
    config.json \
    *.session \
    *.session-journal \
    data/ \
    2>/dev/null || true

echo -e "${GREEN}✓ Резервная копия создана: ${BACKUP_DIR}/${BACKUP_NAME}${NC}"

# Показать размер
SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}" | cut -f1)
echo -e "${YELLOW}Размер: ${SIZE}${NC}"

# Удалить старые бэкапы (старше 30 дней)
echo -e "${YELLOW}Очистка старых бэкапов...${NC}"
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +30 -delete 2>/dev/null || true

# Показать список бэкапов
echo
echo -e "${GREEN}Доступные резервные копии:${NC}"
ls -lh "$BACKUP_DIR"

echo
echo -e "${GREEN}=== Готово! ===${NC}"
