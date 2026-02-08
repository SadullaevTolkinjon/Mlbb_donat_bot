from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import REGULAR_PACKAGES, DOUBLE_PACKAGES, WEEKLY_PASS

def main_menu():
    """Asosiy menyu"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💎 Almaz sotib olish")],
            [KeyboardButton(text="📦 Mening buyurtmalarim")],
            [KeyboardButton(text="ℹ️ Ma'lumot"), KeyboardButton(text="📞 Aloqa")]
        ],
        resize_keyboard=True
    )
    return keyboard

def admin_menu():
    """Admin menyu"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="📦 Buyurtmalar")],
            [KeyboardButton(text="⏳ Kutayotganlar"), KeyboardButton(text="✅ Bajarilganlar")],
            [KeyboardButton(text="👥 Foydalanuvchilar"), KeyboardButton(text="⚙️ Sozlamalar")],
            [KeyboardButton(text="👤 User rejimiga o'tish")]
        ],
        resize_keyboard=True
    )
    return keyboard

def package_categories():
    """Paket kategoriyalari"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Almaz Sotib olish", callback_data="category_regular")],
        [InlineKeyboardButton(text="💎 2x Almaz (Aksiya)", callback_data="category_double")],
        [InlineKeyboardButton(text="🌟 Haftalik Pass", callback_data="category_weekly")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])
    return keyboard

def regular_packages_keyboard():
    """Oddiy paketlar"""
    keyboard = []
    
    for pkg in REGULAR_PACKAGES:
        button = InlineKeyboardButton(
            text=f"💎 {pkg['diamonds']} - {pkg['price']:,} so'm",
            callback_data=f"regular_{pkg['diamonds']}_{pkg['price']}"
        )
        keyboard.append([button])
    
    keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def double_packages_keyboard():
    """2x Aksiya paketlar"""
    keyboard = []
    
    for pkg in DOUBLE_PACKAGES:
        button = InlineKeyboardButton(
            text=f"💎 {pkg['diamonds']}+{pkg['bonus']}={pkg['total']} - {pkg['price']:,} so'm",
            callback_data=f"double_{pkg['total']}_{pkg['price']}"
        )
        keyboard.append([button])
    
    keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def weekly_pass_keyboard():
    """Haftalik/Oylik pass"""
    keyboard = []
    
    for index, pass_item in enumerate(WEEKLY_PASS):
        # Emoji qo'shish
        if "Elite" in pass_item['name']:
            emoji = "✨"
        elif "Epik" in pass_item['name']:
            emoji = "🎯"
        else:
            emoji = "🌟"
        
        button_text = f"{emoji} {pass_item['name']} - {pass_item['price']:,} so'm"
        
        button = InlineKeyboardButton(
            text=button_text,
            callback_data=f"weekly_{index}"  # ← INDEX ishlatish
        )
        keyboard.append([button])
    
    keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def confirm_order_keyboard(order_number: str):
    """Buyurtmani tasdiqlash"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_{order_number}"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")
        ]
    ])
    return keyboard

def admin_order_keyboard(order_number: str):
    """Admin uchun buyurtma klaviaturasi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ To'lovni tasdiqlash", callback_data=f"admin_confirm_{order_number}")],
        [InlineKeyboardButton(text="💎 Yuborildi", callback_data=f"admin_complete_{order_number}")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"admin_cancel_{order_number}")]
    ])
    return keyboard

def settings_menu():
    """Sozlamalar menyusi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Paket narxlari", callback_data="settings_prices")],
        [InlineKeyboardButton(text="💳 To'lov ma'lumoti", callback_data="settings_payment")],
        [InlineKeyboardButton(text="📝 Bot matnlari", callback_data="settings_texts")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings_back")]
    ])
    return keyboard

def package_list_keyboard(packages):
    """Paketlar ro'yxati"""
    keyboard = []
    
    for i, pkg in enumerate(packages):
        if pkg['type'] == 'regular':
            text = f"💎 {pkg['diamonds']} - {pkg['price']:,} so'm"
        elif pkg['type'] == 'double':
            text = f"2X {pkg['diamonds']} - {pkg['price']:,} so'm"
        else:
            text = f"🌟 {pkg.get('name', 'Pass')} - {pkg['price']:,} so'm"
        
        button = InlineKeyboardButton(
            text=text,
            callback_data=f"edit_price_{i}"
        )
        keyboard.append([button])
    
    keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def payment_edit_keyboard():
    """To'lov sozlamalari"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Karta raqami", callback_data="edit_card")],
        [InlineKeyboardButton(text="📱 Telefon", callback_data="edit_phone")],
        [InlineKeyboardButton(text="👤 Ism", callback_data="edit_name")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings_menu")]
    ])
    return keyboard

def texts_edit_keyboard():
    """Matnlar sozlamalari"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👋 Xush kelibsiz matni", callback_data="edit_welcome")],
        [InlineKeyboardButton(text="💳 To'lov matni", callback_data="edit_payment_text")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings_menu")]
    ])
    return keyboard

def delivery_keyboard(order_number: str):
    """Admin uchun yetkazib berish tugmalari"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💎 Yuborildi", 
                callback_data=f"admin_complete_{order_number}"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Rad etish", 
                callback_data=f"admin_cancel_{order_number}"
            )
        ]
    ])
    return keyboard