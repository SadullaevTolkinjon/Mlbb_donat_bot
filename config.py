import os
from dotenv import load_dotenv

load_dotenv()

# Bot sozlamalari
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Admin IDs - .env dan yoki hardcoded
ADMIN_IDS_STR = os.getenv('ADMIN_IDS', '7109486311,7793489555,1958623192')
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(',')]
ADMIN_ID = ADMIN_IDS[0]  # Backward compatibility

# Database
DB_NAME = 'mlbb_bot.db'

# Kanal sozlamalari
CHANNEL_ID = -1002254165405
CHANNEL_USERNAME = "@Retriccomlbb"
CHANNEL_LINK = "https://t.me/Retriccomlbb"
WELCOME_PHOTO = "AgACAgIAAxkBAAMIaYeDzUMxHJ97VFMlBrvgRDX5zDwAArcMaxumLzhIxp6s9zxUpqcBAAMCAAN4AAM6BA"

# Welcome text
WELCOME_TEXT = """
🤝 <b>ASSALOMU ALAYKUM, hurmatli {first_name}!</b>

Bu bot orqali tez va oson MLBB ga donat qilishingiz mumkin.

📢 Kanal: @Retriccomlbb
💬 Aloqa: @Retriccodonat
🤖 Powered by: @sadullaev_tolkinjon
"""

# Order created text
ORDER_CREATED_TEXT = """
✅ <b>Buyurtma qabul qilindi!</b>

📋 Buyurtma raqami: #{order_number}
💎 Paket: {diamonds} Almaz
💰 Summa: {price:,} so'm

💳 <b>TO'LOV MA'LUMOTI:</b>
Karta: <code>{card}</code>
Telefon: <code>{phone}</code>
Nomi: {name}

📸 <b>To'lovdan keyin screenshot yuboring!</b>
"""

# Default paketlar (fallback)
REGULAR_PACKAGES = []
DOUBLE_PACKAGES = []
WEEKLY_PASS = []

# Default to'lov ma'lumoti (fallback)
PAYMENT_CARD = "8600 0000 0000 0000"
PAYMENT_PHONE = "+998 90 000 00 00"
PAYMENT_NAME = "ADMIN"

# Google Sheets dan to'lov ma'lumotini yangilash
def update_payment_info_from_sheets():
    """Google Sheets dan to'lov ma'lumotini yangilash"""
    global PAYMENT_CARD, PAYMENT_PHONE, PAYMENT_NAME
    
    try:
        from sheets import load_payment_info_from_sheets
        payment = load_payment_info_from_sheets()
        
        if payment:
            PAYMENT_CARD = payment.get('card', PAYMENT_CARD)
            PAYMENT_PHONE = payment.get('phone', PAYMENT_PHONE)
            PAYMENT_NAME = payment.get('name', PAYMENT_NAME)
            print("✅ To'lov ma'lumoti Google Sheets dan yangilandi!")
            return True
        else:
            print("⚠️ Google Sheets dan to'lov ma'lumoti bo'sh!")
            return False
            
    except Exception as e:
        print(f"❌ Google Sheets to'lov xatolik: {e}")
        return False

# Google Sheets dan paketlarni yangilash
def update_packages_from_sheets():
    """Google Sheets dan paketlarni yangilash"""
    global REGULAR_PACKAGES, DOUBLE_PACKAGES, WEEKLY_PASS
    
    try:
        from sheets import load_packages_from_sheets
        regular, double, weekly = load_packages_from_sheets()
        
        if regular and double and weekly:
            REGULAR_PACKAGES = regular
            DOUBLE_PACKAGES = double
            WEEKLY_PASS = weekly
            print("✅ Paketlar Google Sheets dan yangilandi!")
            
            # To'lov ma'lumotini ham yangilash
            update_payment_info_from_sheets()
            
            return True
        else:
            print("⚠️ Google Sheets dan ma'lumot bo'sh!")
            return False
            
    except Exception as e:
        print(f"❌ Google Sheets xatolik: {e}")
        return False

# Birinchi yuklash
update_packages_from_sheets()