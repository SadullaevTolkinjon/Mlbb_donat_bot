import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN, update_packages_from_sheets
from database import init_db
import handlers_user
import handlers_admin

logging.basicConfig(level=logging.INFO)

async def update_packages_task():
    """Har 5 daqiqada paketlarni yangilash"""
    while True:
        await asyncio.sleep(300)
        print("🔄 Paketlarni yangilash...")
        update_packages_from_sheets()

async def main():
    """Botni ishga tushirish"""
    print("🚀 Bot ishga tushmoqda...")
    
    await init_db()
    print("✅ Database initialized")
    
    bot = Bot(token=BOT_TOKEN)
    
    # ✅ WEBHOOK NI O'CHIRISH (RAILWAY UCHUN MUHIM!)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook o'chirildi - Polling rejimida ishlamoqda")
    except Exception as e:
        print(f"⚠️ Webhook o'chirishda xatolik: {e}")
    
    dp = Dispatcher()
    
    dp.include_router(handlers_user.router)
    dp.include_router(handlers_admin.router)
    
    asyncio.create_task(update_packages_task())
    
    print("✅ Bot ishga tushdi!")
    print("🔄 Paketlar har 5 daqiqada avtomatik yangilanadi!")
    print("💎 Admin real-time sync enabled!")
    
    # ✅ POLLING (Railway uchun yaxshi ishlaydi)
    await dp.start_polling(bot, skip_updates=False)

if __name__ == '__main__':
    asyncio.run(main())