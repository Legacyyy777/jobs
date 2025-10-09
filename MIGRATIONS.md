# Миграции базы данных

## Автоматические миграции

Все миграции выполняются **автоматически при запуске бота** в функции `db.init_tables()`.

### ✅ Безопасность

- Все миграции используют `IF NOT EXISTS` / `IF EXISTS` - безопасны для повторного запуска
- Существующие данные **НЕ изменяются**
- Существующие таблицы **НЕ пересоздаются**
- Только добавляются новые колонки с значениями по умолчанию

---

## История миграций

### Миграция 1: Профессии пользователей
**Дата:** Начальная версия

**Изменения:**
- Добавлена колонка `profession` в таблицу `users`
- Тип: `VARCHAR(20)` 
- Значение по умолчанию: `'painter'`
- Обновлены существующие записи: `profession = 'painter'`

**SQL:**
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS profession VARCHAR(20) DEFAULT 'painter';
UPDATE users SET profession = 'painter' WHERE profession IS NULL;
```

---

### Миграция 2: Поддержка пескоструйщиков и супортов
**Дата:** Обновление для пескоструйщиков

**Изменения в таблице `orders`:**
- `suspensia_type VARCHAR(20)` - тип супортов (paint/logo)
- `quantity INTEGER DEFAULT 1` - количество супортов
- `spraying_deep INTEGER DEFAULT 0` - количество глубоких напылений
- `spraying_shallow INTEGER DEFAULT 0` - количество неглубоких напылений
- Колонка `size` теперь может быть NULL (для супортов и насадок)

**SQL:**
```sql
ALTER TABLE orders ADD COLUMN IF NOT EXISTS suspensia_type VARCHAR(20);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 1;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS spraying_deep INTEGER DEFAULT 0;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS spraying_shallow INTEGER DEFAULT 0;
ALTER TABLE orders ALTER COLUMN size DROP NOT NULL;
```

---

### Миграция 3: Система напоминаний
**Дата:** Добавление автоматических напоминаний

**Изменения в таблице `orders`:**
- `reminder_sent BOOLEAN DEFAULT FALSE` - флаг отправки напоминания
- `reminder_message_id BIGINT` - ID сообщения с напоминанием для удаления

**SQL:**
```sql
ALTER TABLE orders ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN DEFAULT FALSE;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS reminder_message_id BIGINT;
```

**Функционал:**
- Автоматическое напоминание модераторам через 30 минут
- Удаление напоминания при подтверждении/отклонении заказа

---

### Миграция 4: Очистка дублирующих полей
**Дата:** Рефакторинг структуры

**Изменения:**
- Удалена колонка `profession` из таблицы `orders` (дублировалась из `users`)
- Удалено ограничение уникальности `orders_order_number_key`
- Уникальность номеров контролируется на уровне приложения с учётом профессии

**SQL:**
```sql
ALTER TABLE orders DROP COLUMN IF EXISTS profession;
ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_order_number_key;
```

---

## Индексы

Для оптимизации запросов созданы следующие индексы:

```sql
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
```

---

## Проверка миграций

При запуске бота вы увидите в логах:

```
🔄 Выполнение миграций базы данных...
✅ Миграция: добавлена колонка profession в таблицу users
✅ Миграция: добавлены колонки для пескоструйщика и супортов
✅ Миграция: добавлены колонки для системы напоминаний
✅ Все миграции выполнены успешно
```

---

## Откат миграций

**⚠️ ВНИМАНИЕ:** Откат миграций может привести к потере данных!

Если необходимо откатить миграции:

```sql
-- Откат миграции 3 (напоминания)
ALTER TABLE orders DROP COLUMN IF EXISTS reminder_sent;
ALTER TABLE orders DROP COLUMN IF EXISTS reminder_message_id;

-- Откат миграции 2 (пескоструйщики)
ALTER TABLE orders DROP COLUMN IF EXISTS suspensia_type;
ALTER TABLE orders DROP COLUMN IF EXISTS quantity;
ALTER TABLE orders DROP COLUMN IF EXISTS spraying_deep;
ALTER TABLE orders DROP COLUMN IF EXISTS spraying_shallow;

-- Откат миграции 1 (профессии)
ALTER TABLE users DROP COLUMN IF EXISTS profession;
```

---

## Совместимость

- ✅ PostgreSQL 12+
- ✅ Все миграции идемпотентны (можно запускать многократно)
- ✅ Обратная совместимость с существующими данными
- ✅ Нет downtime при обновлении

