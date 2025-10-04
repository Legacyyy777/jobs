-- Создание базы данных painter_bot (если не существует)
SELECT 'CREATE DATABASE painter_bot'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'painter_bot')\gexec

-- Подключение к базе данных painter_bot
\c painter_bot;

-- Создание расширений если нужно
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Установка правильной кодировки
SET client_encoding = 'UTF8';
