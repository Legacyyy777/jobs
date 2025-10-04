#!/bin/bash

echo "🔧 Тестирование исправлений"
echo "============================="

echo "📋 Текущий статус контейнеров:"
docker-compose ps

echo ""
echo "🔄 Перезапуск бота с исправлениями..."
docker-compose restart bot

echo ""
echo "⏳ Ожидание 10 секунд..."
sleep 10

echo ""
echo "📋 Логи бота (последние 30 строк):"
docker logs painter_bot --tail 30

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
echo "🎯 Тест завершен!"
