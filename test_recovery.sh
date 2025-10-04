#!/bin/bash

echo "🧪 Тестирование восстановления после docker compose down -v"
echo "============================================================="

echo "📋 Текущий статус:"
docker-compose ps

echo ""
echo "🛑 Остановка и очистка volumes..."
docker-compose down -v

echo ""
echo "⏳ Ожидание 3 секунды..."
sleep 3

echo ""
echo "🚀 Запуск системы..."
docker-compose up -d

echo ""
echo "⏳ Ожидание инициализации (30 секунд)..."
sleep 30

echo ""
echo "📊 Проверка статуса контейнеров:"
docker-compose ps

echo ""
echo "📋 Логи базы данных (последние 20 строк):"
docker logs painter_bot_db --tail 20

echo ""
echo "📋 Логи бота (последние 20 строк):"
docker logs painter_bot --tail 20

echo ""
echo "🔍 Проверка базы данных:"
if docker exec painter_bot_db psql -U postgres -d painter_bot -c "SELECT COUNT(*) FROM users;" > /dev/null 2>&1; then
    echo "✅ База данных painter_bot доступна"
    USER_COUNT=$(docker exec painter_bot_db psql -U postgres -d painter_bot -tAc "SELECT COUNT(*) FROM users;")
    ORDER_COUNT=$(docker exec painter_bot_db psql -U postgres -d painter_bot -tAc "SELECT COUNT(*) FROM orders;")
    echo "   - Пользователей: $USER_COUNT"
    echo "   - Заказов: $ORDER_COUNT"
else
    echo "❌ База данных painter_bot недоступна"
fi

echo ""
echo "🔍 Проверка таблиц:"
if docker exec painter_bot_db psql -U postgres -d painter_bot -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';" > /dev/null 2>&1; then
    TABLES=$(docker exec painter_bot_db psql -U postgres -d painter_bot -tAc "SELECT string_agg(tablename, ', ') FROM pg_tables WHERE schemaname = 'public';")
    echo "✅ Таблицы созданы: $TABLES"
else
    echo "❌ Таблицы не найдены"
fi

echo ""
echo "🎯 Тест завершен!"
echo ""
echo "💡 Если что-то не работает, попробуйте:"
echo "   docker-compose restart"
echo "   docker logs painter_bot --tail 50"
