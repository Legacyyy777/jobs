#!/bin/bash

# Скрипт восстановления базы данных для painter_bot

echo "🔧 Скрипт восстановления базы данных painter_bot"
echo "================================================"

# Функция для проверки статуса контейнеров
check_containers() {
    echo "📋 Проверка статуса контейнеров..."
    docker ps -a | grep -E "(painter_bot|postgres)"
}

# Функция для перезапуска базы данных
restart_database() {
    echo "🔄 Перезапуск базы данных..."
    docker-compose stop db
    sleep 5
    docker-compose up -d db
    
    echo "⏳ Ожидание готовности базы данных..."
    sleep 10
    
    # Проверяем готовность базы данных
    for i in {1..30}; do
        if docker exec painter_bot_db pg_isready -U postgres -d painter_bot > /dev/null 2>&1; then
            echo "✅ База данных готова к работе"
            return 0
        fi
        echo "⏳ Ожидание... ($i/30)"
        sleep 2
    done
    
    echo "❌ База данных не готова после 60 секунд ожидания"
    return 1
}

# Функция для очистки и пересоздания базы данных
recreate_database() {
    echo "⚠️ ВНИМАНИЕ: Это приведет к потере всех данных!"
    read -p "Вы уверены? Введите 'yes' для подтверждения: " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo "❌ Операция отменена"
        return 1
    fi
    
    echo "🔄 Остановка всех сервисов..."
    docker-compose down
    
    echo "🗑️ Удаление данных базы данных..."
    docker volume rm jobs_postgres_data 2>/dev/null || true
    
    echo "🚀 Запуск сервисов заново..."
    docker-compose up -d
    
    echo "⏳ Ожидание готовности..."
    sleep 15
    
    echo "✅ База данных пересоздана"
}

# Функция для запуска диагностики
run_diagnostics() {
    echo "🔍 Запуск диагностики базы данных..."
    
    if [ ! -f ".env" ]; then
        echo "❌ Файл .env не найден"
        return 1
    fi
    
    # Запускаем Python скрипт диагностики
    docker exec painter_bot python db_recovery.py
}

# Функция для просмотра логов
view_logs() {
    echo "📋 Логи базы данных (последние 50 строк):"
    docker logs painter_bot_db --tail 50
    
    echo ""
    echo "📋 Логи бота (последние 50 строк):"
    docker logs painter_bot --tail 50
}

# Функция для подключения к базе данных
connect_to_db() {
    echo "🔌 Подключение к базе данных..."
    docker exec -it painter_bot_db psql -U postgres -d painter_bot
}

# Главное меню
show_menu() {
    echo ""
    echo "Выберите действие:"
    echo "1) Проверить статус контейнеров"
    echo "2) Перезапустить базу данных"
    echo "3) Пересоздать базу данных (ПОТЕРЯ ДАННЫХ!)"
    echo "4) Запустить диагностику"
    echo "5) Просмотреть логи"
    echo "6) Подключиться к базе данных"
    echo "7) Перезапустить все сервисы"
    echo "8) Выход"
    echo ""
}

# Основной цикл
while true; do
    show_menu
    read -p "Введите номер действия: " choice
    
    case $choice in
        1)
            check_containers
            ;;
        2)
            restart_database
            ;;
        3)
            recreate_database
            ;;
        4)
            run_diagnostics
            ;;
        5)
            view_logs
            ;;
        6)
            connect_to_db
            ;;
        7)
            echo "🔄 Перезапуск всех сервисов..."
            docker-compose restart
            ;;
        8)
            echo "👋 До свидания!"
            exit 0
            ;;
        *)
            echo "❌ Неверный выбор"
            ;;
    esac
    
    echo ""
    read -p "Нажмите Enter для продолжения..."
done
