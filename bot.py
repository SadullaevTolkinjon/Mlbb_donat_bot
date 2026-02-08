import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN, update_packages_from_sheets
from database import init_db
import handlers_user
import handlers_admin

# Logging
logging.basicConfig(level=logging.INFO)

async def update_packages_task():
    """Har 5 daqiqada paketlarni yangilash"""
    while True:
        await asyncio.sleep(300)  # 5 daqiqa = 300 sekund
        print("🔄 Paketlarni yangilash...")
        update_packages_from_sheets()

async def main():
    """Botni ishga tushirish"""
    print("🚀 Bot ishga tushmoqda...")
    
    # Database yaratish
    await init_db()
    
    # Bot va Dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Handlerlarni registratsiya qilish
    dp.include_router(handlers_user.router)
    dp.include_router(handlers_admin.router)
    
    # Avtomatik yangilanish taskini boshlash
    asyncio.create_task(update_packages_task())
    
    # Botni ishga tushirish
    print("✅ Bot ishga tushdi!")
    print("🔄 Paketlar har 5 daqiqada avtomatik yangilanadi!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())