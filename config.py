import os
from dotenv import load_dotenv

load_dotenv()

# Bot sozlamalari
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
ADMIN_IDS = [7109486311, 7793489555,1958623192]



# Database
DB_NAME = 'mlbb_bot.db'

# Paketlar (Diamonds va Narx)
# PACKAGES ni o'chirib, quyidagilarni yozing:

# Oddiy paketlar
REGULAR_PACKAGES = [
    {"diamonds": 50, "price": 12000},
    {"diamonds": 86, "price": 17000},
    {"diamonds": 165, "price": 32000},
    {"diamonds": 172, "price": 34000},
    {"diamonds": 257, "price": 48000},
    {"diamonds": 275, "price": 50000},
    {"diamonds": 565, "price": 105000},
    {"diamonds": 706, "price": 130000},
    {"diamonds": 2195, "price": 380000},
    {"diamonds": 3688, "price": 610000},
    {"diamonds": 5532, "price": 930000},
    {"diamonds": 9288, "price": 1500000},
]

# 2x Aksiya paketlar (1 marta)
DOUBLE_PACKAGES = [
    {"diamonds": 50, "bonus": 50, "total": 100, "price": 12000},
    {"diamonds": 150, "bonus": 150, "total": 300, "price": 32000},
    {"diamonds": 250, "bonus": 250, "total": 500, "price": 50000},
    {"diamonds": 500, "bonus": 500, "total": 1000, "price": 105000},
]

# Haftalik pass
# Haftalik va Oylik to'plamlar
WEEKLY_PASS = [
    {
        "name": "Haftalik Elite to'plam", 
        "price": 12000,
        "description": "💎55 + ⭐20 + ⭐2",
        "period": "haftalik"
    },
    {
        "name": "Haftalik almaz obunasi", 
        "price": 20000,
        "description": "Haftalik almaz",
        "period": "haftalik"
    },
    {
        "name": "Oylik Epik to'plam", 
        "price": 53000,
        "description": "💎275 + ⭐180 + ⭐10",
        "period": "oylik"
    },
    {
        "name": "Twinlight pass", 
        "price": 100000,
        "description": "Premium pass",
        "period": "oylik"
    },
]

# Xabarlar
WELCOME_TEXT = """
🎮 <b>MLBB Donat Bot ga xush kelibsiz!</b>

💎 Mobile Legends almaz sotib oling!
⚡ Tez va ishonchli xizmat!

Boshlash uchun quyidagi tugmani bosing 👇
"""

ORDER_CREATED_TEXT = """
✅ <b>Buyurtma qabul qilindi!</b>

📋 Buyurtma raqami: #{order_number}
💎 Paket: {diamonds} Almaz
💰 Summa: {price:,} so'm

💳 <b>To'lov ma'lumoti:</b>
Karta: <code>{card}</code>
Telefon: <code>{phone}</code>
Nomi: {name}

📸 <b>To'lovdan keyin screenshot yuboring!</b>
"""


CHANNEL_ID = -1002254165405
CHANNEL_USERNAME = "@Retriccomlbb"
CHANNEL_LINK = "https://t.me/Retriccomlbb"
WELCOME_PHOTO = "AgACAgIAAxkBAAMIaYeDzUMxHJ97VFMlBrvgRDX5zDwAArcMaxumLzhIxp6s9zxUpqcBAAMCAAN4AAM6BA"
WELCOME_TEXT = """
🤝 <b>ASSALOMU ALAYKUM, hurmatli {first_name}!</b>

Bu bot orqali tez va oson MLBB ga donat qilishingiz mumkin.

📢 Kanal: @Retriccomlbb
💬 Aloqa: @Retriccodonat
🤖 Powered by: @sadullaev_tolkinjon
"""
# Default paketlar (fallback)
REGULAR_PACKAGES = []
DOUBLE_PACKAGES = []
WEEKLY_PASS = []

# Default to'lov ma'lumoti (fallback)
PAYMENT_CARD = "8600 0000 0000 0000"
PAYMENT_PHONE = "+998 90 000 00 00"
PAYMENT_NAME = "ADMIN"

# Google Sheets dan yuklash funksiyasi
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