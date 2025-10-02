# Быстрый запуск бота

## 1. Настройка

```bash
# Скопируйте пример конфигурации
cp env.example .env

# Отредактируйте .env файл
nano .env
```

**Обязательно укажите в .env:**
- `BOT_TOKEN` - токен от @BotFather
- `ADMIN_CHAT_ID` - ваш Telegram ID (узнать у @userinfobot)

## 2. Запуск

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка логов
docker-compose logs -f bot
```

## 3. Проверка работы

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Нажмите кнопку "🎨 Создать заказ"
4. Отправьте фото диска
5. Пройдите весь процесс создания заказа через кнопки
6. Проверьте, что админ получил уведомление

## 4. Остановка

```bash
docker-compose down
```

## 5. Обновление

```bash
# Остановить
docker-compose down

# Обновить код
git pull

# Пересобрать и запустить
docker-compose up -d --build
```

## Полезные команды

```bash
# Просмотр логов базы данных
docker-compose logs db

# Подключение к базе данных
docker-compose exec db psql -U postgres -d painter_bot

# Перезапуск только бота
docker-compose restart bot

# Просмотр статуса сервисов
docker-compose ps
```
