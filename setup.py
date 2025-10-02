#!/usr/bin/env python3
"""
Скрипт для быстрой настройки бота
"""
import os
import shutil

def setup_env():
    """Создает .env файл из примера"""
    if os.path.exists('.env'):
        print("❌ Файл .env уже существует!")
        response = input("Перезаписать? (y/N): ")
        if response.lower() != 'y':
            print("Отменено.")
            return
    
    if not os.path.exists('env.example'):
        print("❌ Файл env.example не найден!")
        return
    
    shutil.copy('env.example', '.env')
    print("✅ Файл .env создан из env.example")
    print("\n📝 Не забудьте отредактировать .env файл:")
    print("   - BOT_TOKEN - токен от @BotFather")
    print("   - ADMIN_CHAT_ID - ваш Telegram ID")

def main():
    print("🤖 Настройка телеграм-бота для маляров")
    print("=" * 40)
    
    setup_env()
    
    print("\n🚀 Для запуска выполните:")
    print("   docker-compose up -d")
    
    print("\n📖 Подробная документация в README.md")

if __name__ == "__main__":
    main()
