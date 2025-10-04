-- Инициализация базы данных painter_bot
-- Этот файл выполняется автоматически при первом запуске PostgreSQL

-- Создание базы данных painter_bot (если не существует)
SELECT 'CREATE DATABASE painter_bot'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'painter_bot')\gexec

-- Подключение к базе данных painter_bot
\c painter_bot;

-- Создание расширений если нужно
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Установка правильной кодировки
SET client_encoding = 'UTF8';

-- Создание таблиц (если не существуют)
-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    profession VARCHAR(20) DEFAULT 'painter',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица заказов
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    set_type VARCHAR(20) NOT NULL,
    size VARCHAR(10),
    alumochrome BOOLEAN DEFAULT FALSE,
    suspensia_type VARCHAR(20),
    quantity INTEGER DEFAULT 1,
    spraying_deep INTEGER DEFAULT 0,
    spraying_shallow INTEGER DEFAULT 0,
    price INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    photo_file_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);

-- Логирование успешной инициализации
\echo 'База данных painter_bot успешно инициализирована'
