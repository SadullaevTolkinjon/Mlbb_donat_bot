from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import re

from config import WELCOME_TEXT, ORDER_CREATED_TEXT, PAYMENT_CARD, PAYMENT_PHONE, PAYMENT_NAME, ADMIN_IDS, CHANNEL_ID, CHANNEL_USERNAME, CHANNEL_LINK, WELCOME_PHOTO
from keyboards import main_menu, confirm_order_keyboard
from database import add_user, create_order, update_screenshot, get_statistics, save_admin_notification  # ✅ QOSHILDI

router = Router()

# States
class OrderStates(StatesGroup):
    waiting_for_id_and_zone = State()

# Vaqtinchalik data
temp_orders = {}

@router.message(CommandStart())
async def cmd_start(message: Message, bot):
    """Start command handler"""
    print(f"✅ Start command from user: {message.from_user.id}")
    
    # Admin kanal tekshiruvidan o'tkazilmaydi
    if message.from_user.id not in ADMIN_IDS:
        # Kanal a'zoligini tekshirish
        try:
            member = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)
            if member.status in ['left', 'kicked']:
                # Kanal a'zosi emas
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📢 Kanalga qo'shilish", url=CHANNEL_LINK)],
                    [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subscription")]
                ])
                
                # Rasm + matn
                welcome_text = WELCOME_TEXT.format(first_name=message.from_user.first_name)
                
                await bot.send_photo(
                    chat_id=message.from_user.id,
                    photo=WELCOME_PHOTO,
                    caption=(
                        f"{welcome_text}\n\n"
                        "⚠️ <b>Botdan foydalanish uchun kanalga qo'shiling!</b>\n\n"
                        "Qo'shilganingizdan keyin '✅ Tekshirish' tugmasini bosing."
                    ),
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                return
        except Exception as e:
            print(f"❌ Kanal tekshiruvida xatolik: {e}")
    
    # User qo'shish
    await add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or ""
    )
    
    # Admin yoki oddiy user?
    if message.from_user.id in ADMIN_IDS:
        # Admin uchun
        from keyboards import admin_menu
        await message.answer(
            text="👨‍💼 <b>Admin Panel</b>\n\nXush kelibsiz!",
            reply_markup=admin_menu(),
            parse_mode="HTML"
        )
    else:
        # Oddiy user uchun
        welcome_text = WELCOME_TEXT.format(first_name=message.from_user.first_name)
        
        # Rasm + matn
        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=WELCOME_PHOTO,
            caption=welcome_text,
            parse_mode="HTML"
        )
        
        # Keyboard
        await message.answer(
            text="Quyidagi tugmalardan foydalaning:",
            reply_markup=main_menu()
        )
    
    print("✅ Welcome message sent!")

@router.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery, bot):
    """Kanal a'zoligini tekshirish"""
    user_id = callback.from_user.id
    
    # Admin emas
    if user_id in ADMIN_IDS:
        await callback.answer("Siz adminsiz!")
        return
    
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        
        if member.status in ['member', 'administrator', 'creator']:
            # A'zo bo'lgan
            await add_user(
                telegram_id=user_id,
                username=callback.from_user.username or "",
                first_name=callback.from_user.first_name or ""
            )
            
            welcome_text = WELCOME_TEXT.format(first_name=callback.from_user.first_name)
            
            # Rasmni yangilash
            await callback.message.edit_caption(
                caption=f"{welcome_text}\n\n✅ <b>Kanalga qo'shilganingiz tasdiqlandi!</b>",
                parse_mode="HTML"
            )
            
            # Keyboard yuborish
            await callback.message.answer(
                text="Quyidagi tugmalardan foydalaning:",
                reply_markup=main_menu()
            )
            
            await callback.answer("✅ Xush kelibsiz!")
        else:
            # Hali a'zo emas
            await callback.answer(
                "❌ Siz hali kanalga qo'shilmagansiz!\n"
                "Iltimos, avval kanalga qo'shiling.",
                show_alert=True
            )
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        await callback.answer("❌ Xatolik! Qaytadan urinib ko'ring.")

@router.message(F.text == "💎 Almaz sotib olish")
async def show_packages(message: Message, state: FSMContext):
    """Paket kategoriyalari"""
    await state.clear()
    
    print("✅ Packages button clicked")
    from keyboards import package_categories
    await message.answer(
        "💎 <b>Menyu yordamida kerakli variantni tanlang:</b>",
        reply_markup=package_categories(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "category_regular")
async def show_regular_packages(callback: CallbackQuery):
    """Oddiy paketlar"""
    from keyboards import regular_packages_keyboard
    await callback.message.edit_text(
        "💎 <b>Oddiy Almaz paketlari:</b>\n\n"
        "Paketni tanlang 👇",
        reply_markup=regular_packages_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "category_double")
async def show_double_packages(callback: CallbackQuery):
    """2x paketlar"""
    from keyboards import double_packages_keyboard
    await callback.message.edit_text(
        "2️⃣✖️ <b>2X ALMAZ AKSIYASI!</b>\n\n"
        "💎500+500=💎1000\n"
        "💎250+250=💎500\n"
        "💎150+150=💎300\n"
        "💎50+50=💎100\n\n"
        "⚠️ <b>BU AKSIYA FAQAT 1TA ACCAUNTGA 1 MARTA</b>\n"
        "(Har biridan 1 donadan)\n"
        "Avval olganlar uchun ishlamaydi!\n\n"
        "Paketni tanlang 👇",
        reply_markup=double_packages_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "category_weekly")
async def show_weekly_pass(callback: CallbackQuery):
    """Haftalik/Oylik pass"""
    from keyboards import weekly_pass_keyboard
    from config import WEEKLY_PASS
    
    # Dynamic matn yaratish
    text = "🌟 <b>HAFTALIK VA OYLIK TO'PLAMLAR:</b>\n\n"
    
    for item in WEEKLY_PASS:
        if "Elite" in item['name']:
            emoji = "✨"
        elif "Epik" in item['name']:
            emoji = "🎯"
        else:
            emoji = "🌟"
        
        description = item.get('description', '')
        period_text = "1 haftada 1 marta" if item['period'] == 'haftalik' else "1 oyda 1 marta"
        
        text += (
            f"{emoji} <b>{item['name']}:</b> {item['price']:,} so'm\n"
            f"{description} ({period_text})\n\n"
        )
    
    text += "⚠️ Har bir to'plam faqat 1 marta olinadi!\n\n"
    text += "To'plamni tanlang 👇"
    
    await callback.message.edit_text(
        text,
        reply_markup=weekly_pass_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.regexp(r'^weekly_\d+$'))
async def select_weekly_pass(callback: CallbackQuery, state: FSMContext):
    """Haftalik/Oylik pass tanlash"""
    try:
        index = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("❌ Xatolik!")
        return
    
    from config import WEEKLY_PASS
    
    if index >= len(WEEKLY_PASS):
        await callback.answer("❌ Paket topilmadi!")
        return
    
    pass_item = WEEKLY_PASS[index]
    pass_name = pass_item['name']
    price = pass_item['price']
    description = pass_item.get('description', '')
    
    temp_orders[callback.from_user.id] = {
        "type": "weekly",
        "diamonds": 0,
        "price": price,
        "pass_name": pass_name,
        "description": description
    }
    
    await callback.message.edit_text(
        f"📦 <b>Siz tanladingiz:</b>\n\n"
        f"🌟 {pass_name}\n"
        f"📝 {description}\n"
        f"💰 {price:,} so'm\n\n"
        f"Paketni tasdiqlab, ID/SERVER kiriting.\n\n"
        f"📌 <b>Avvalo ID va SERVER yuboring:</b>\n\n"
        f"<code>123456789 3333</code>\n"
        f"yoki\n"
        f"<code>123456789 (3333)</code>\n\n"
        f"‼️ <b>ID va Server toʻgʻri kiritilganiga ishonch hosil qiling.</b>",
        parse_mode="HTML"
    )
    
    await state.set_state(OrderStates.waiting_for_id_and_zone)
    await callback.answer()

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery):
    """Kategoriyalarga qaytish"""
    from keyboards import package_categories
    await callback.message.edit_text(
        "💎 <b>Menyu yordamida kerakli variantni tanlang:</b>",
        reply_markup=package_categories(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("regular_"))
async def select_regular_package(callback: CallbackQuery, state: FSMContext):
    """Oddiy paket tanlash"""
    _, diamonds, price = callback.data.split("_")
    
    temp_orders[callback.from_user.id] = {
        "type": "regular",
        "diamonds": int(diamonds),
        "price": int(price)
    }
    
    await callback.message.edit_text(
        f"📦 <b>Siz tanladingiz:</b> {diamonds} 💎 - {int(price):,} so'm\n\n"
        f"Paketni tasdiqlab, ID/SERVER kiriting.\n\n"
        f"📌 <b>Avvalo ID va SERVER yuboring:</b>\n\n"
        f"<code>123456789 3333</code>\n"
        f"yoki\n"
        f"<code>123456789 (3333)</code>\n\n"
        f"‼️ <b>ID va Server toʻgʻri kiritilganiga ishonch hosil qiling.</b>",
        parse_mode="HTML"
    )
    
    await state.set_state(OrderStates.waiting_for_id_and_zone)
    await callback.answer()

@router.callback_query(F.data.startswith("double_"))
async def select_double_package(callback: CallbackQuery, state: FSMContext):
    """2x paket tanlash"""
    _, total, price = callback.data.split("_")
    
    temp_orders[callback.from_user.id] = {
        "type": "double",
        "diamonds": int(total),
        "price": int(price)
    }
    
    await callback.message.edit_text(
        f"📦 <b>Siz tanladingiz:</b> 2X {total} 💎 - {int(price):,} so'm\n\n"
        f"⚠️ <b>Bu aksiya faqat 1 marta!</b>\n\n"
        f"Paketni tasdiqlab, ID/SERVER kiriting.\n\n"
        f"📌 <b>Avvalo ID va SERVER yuboring:</b>\n\n"
        f"<code>123456789 3333</code>\n"
        f"yoki\n"
        f"<code>123456789 (3333)</code>\n\n"
        f"‼️ <b>ID va Server toʻgʻri kiritilganiga ishonch hosil qiling.</b>",
        parse_mode="HTML"
    )
    
    await state.set_state(OrderStates.waiting_for_id_and_zone)
    await callback.answer()

@router.message(OrderStates.waiting_for_id_and_zone)
async def get_id_and_zone(message: Message, state: FSMContext):
    """ID va Zone ID ni birga qabul qilish"""
    text = message.text.strip()
    
    pattern = r'^(\d{6,12})\s*[\(\s]+(\d{2,5})[\)\s]*$'
    match = re.match(pattern, text)
    
    if not match:
        await message.answer(
            "❎ <b>Неверный формат. Отправьте ID и SERVER в формате:</b>\n\n"
            "<code>123456789 1234</code>\n"
            "(или <code>123456789 (1234)</code>)",
            parse_mode="HTML"
        )
        return
    
    player_id = match.group(1)
    zone_id = match.group(2)
    
    order_data = temp_orders[message.from_user.id]
    order_data["player_id"] = player_id
    order_data["zone_id"] = zone_id
    
    package_type = order_data.get('type', 'regular')
    if package_type == 'weekly':
        package_text = f"🌟 {order_data.get('pass_name', 'Haftalik Pass')}"
    else:
        package_text = f"💎 {order_data['diamonds']} Almaz"
    
    await message.answer(
        f"📋 <b>Buyurtmani tasdiqlang:</b>\n\n"
        f"📦 Paket: {package_text}\n"
        f"💰 Narx: {order_data['price']:,} so'm\n"
        f"🆔 Player ID: <code>{player_id}</code>\n"
        f"🌍 Zone ID: <code>{zone_id}</code>\n\n"
        f"Davom etamizmi?",
        reply_markup=confirm_order_keyboard("temp"),
        parse_mode="HTML"
    )
    
    await state.clear()

@router.callback_query(F.data.startswith("confirm_"))
async def confirm_order(callback: CallbackQuery, bot):
    """Tasdiqlash"""
    user_id = callback.from_user.id
    
    if user_id not in temp_orders:
        await callback.answer("❌ Xatolik!")
        return
    
    order_data = temp_orders[user_id]
    
    order_number = await create_order(
        user_id=user_id,
        diamonds=order_data["diamonds"],
        price=order_data["price"],
        player_id=order_data["player_id"],
        zone_id=order_data["zone_id"]
    )
    
    temp_orders[user_id]["order_number"] = order_number
    
    payment_text = ORDER_CREATED_TEXT.format(
        order_number=order_number,
        diamonds=order_data["diamonds"],
        price=order_data["price"],
        card=PAYMENT_CARD,
        phone=PAYMENT_PHONE,
        name=PAYMENT_NAME
    )
    
    await callback.message.edit_text(payment_text, parse_mode="HTML")
    await callback.message.answer("📸 <b>Screenshot yuborishni kutmoqdamiz...</b>", parse_mode="HTML")
    await callback.answer()

@router.message(F.photo)
async def receive_screenshot(message: Message, bot):
    """Screenshot yoki Photo ID olish"""
    user_id = message.from_user.id
    
    # Admin file_id olmoqchi
    if user_id in ADMIN_IDS:
        file_id = message.photo[-1].file_id
        await message.answer(
            f"📸 <b>Photo File ID:</b>\n\n"
            f"<code>{file_id}</code>\n\n"
            "Ushbu ID ni <code>config.py</code> da "
            "<code>WELCOME_PHOTO</code> ga qo'ying.",
            parse_mode="HTML"
        )
        return
    
    # Oddiy user - screenshot
    if user_id not in temp_orders or "order_number" not in temp_orders[user_id]:
        await message.answer("❌ Avval buyurtma bering!")
        return
    
    order_number = temp_orders[user_id]["order_number"]
    order_data = temp_orders[user_id]
    file_id = message.photo[-1].file_id
    
    await update_screenshot(order_number, file_id)
    
    await message.answer(
        f"✅ <b>Screenshot qabul qilindi!</b>\n\n"
        f"📋 Buyurtma: #{order_number}\n"
        f"⏳ Admin tekshiryapti...\n\n"
        f"Tez orada almaz yuboriladi! 💎",
        parse_mode="HTML"
    )
    
    from keyboards import admin_order_keyboard
    
    # Paket turini aniqlash
    package_type = order_data.get('type', 'regular')
    if package_type == 'double':
        package_info = f"2X {order_data['diamonds']} 💎"
    elif package_type == 'weekly':
        pass_name = order_data.get('pass_name', 'Pass')
        description = order_data.get('description', '')
        if description:
            package_info = f"🌟 {pass_name}\n📝 {description}"
        else:
            package_info = f"🌟 {pass_name}"
    else:
        package_info = f"{order_data['diamonds']} 💎"
    
    id_format = f"{order_data['player_id']} ({order_data['zone_id']})"

    admin_text = (
        f"🔔 <b>YANGI BUYURTMA!</b>\n\n"
        f"📋 Buyurtma: #{order_number}\n"
        f"👤 User: @{message.from_user.username or 'username_yoq'}\n"
        f"💎 Paket: {package_info}\n"
        f"💰 Summa: {order_data['price']:,} so'm\n"
        f"🆔 ID: <code>{id_format}</code>\n\n"
        f"📸 Screenshot:"
    )
    
    # ✅ BARCHA ADMINLARGA YUBORISH VA MESSAGE_ID SAQLASH
    for admin_id in ADMIN_IDS:
        try:
            sent_message = await bot.send_photo(
                chat_id=admin_id,
                photo=file_id,
                caption=admin_text,
                reply_markup=admin_order_keyboard(order_number),
                parse_mode="HTML"
            )
            
            # ✅ MESSAGE_ID NI SAQLASH
            await save_admin_notification(order_number, admin_id, sent_message.message_id)
            print(f"✅ Admin {admin_id} ga yuborildi, message_id={sent_message.message_id}")
            
        except Exception as e:
            print(f"❌ Admin {admin_id} ga yuborib bo'lmadi: {e}")
    
    del temp_orders[user_id]

@router.callback_query(F.data == "cancel")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    """Bekor qilish"""
    await state.clear()
    if callback.from_user.id in temp_orders:
        del temp_orders[callback.from_user.id]
    await callback.message.edit_text("❌ Bekor qilindi!")
    await callback.answer()

@router.message(F.text == "📦 Mening buyurtmalarim")
async def my_orders(message: Message, state: FSMContext):
    """Foydalanuvchi buyurtmalari"""
    await state.clear()
    
    from database import get_user_orders
    
    orders = await get_user_orders(message.from_user.id)
    
    if not orders:
        await message.answer(
            "📦 <b>Sizda hali buyurtmalar yo'q</b>\n\n"
            "💎 Almaz sotib olish uchun tugmani bosing!",
            parse_mode="HTML"
        )
        return
    
    text = "📦 <b>MENING BUYURTMALARIM:</b>\n\n"
    
    for order in orders:
        order_number = order[1]
        diamonds = order[3]
        price = order[4]
        status = order[8]
        created_at = order[9]
        
        if status == 'completed':
            status_emoji = '✅'
            status_text = 'Bajarildi'
        elif status == 'payment_confirmed':
            status_emoji = '⏳'
            status_text = 'Jarayonda'
        elif status == 'screenshot_sent':
            status_emoji = '🔍'
            status_text = 'Tekshirilmoqda'
        else:
            status_emoji = '⏳'
            status_text = 'Kutilmoqda'
        
        text += (
            f"{status_emoji} <b>#{order_number}</b>\n"
            f"💎 {diamonds} Almaz\n"
            f"💰 {price:,} so'm\n"
            f"📅 {created_at[:16]}\n"
            f"Status: {status_text}\n"
            f"─────────────\n"
        )
    
    if len(orders) == 20:
        text += "\n📝 Faqat so'ngi 20 ta ko'rsatildi"
    
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "ℹ️ Ma'lumot")
async def info(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        "ℹ️ <b>Bot haqida:</b>\n\n"
        "🎮 MLBB Almazlar\n"
        "⚡ Tez va ishonchli\n\n"
        "📞 @Retriccodonat",
        parse_mode="HTML"
    )

@router.message(F.text == "📞 Aloqa")
async def contact(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        "📞 <b>Bog'lanish:</b>\n\n"
        "👨‍💼 @Retriccodonat\n"
        "📱 +998 88 112 70 00",
        parse_mode="HTML"
    )

# ========== ADMIN FUNKSIYALARI ==========

@router.message(F.text == "👤 User rejimiga o'tish")
async def switch_to_user_mode(message: Message):
    """Admin user rejimiga o'tadi"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
    await message.answer(
        text=WELCOME_TEXT,
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "📊 Statistika")
async def admin_stats(message: Message):
    """Statistika (admin)"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
    try:
        from database import get_statistics
        stats = await get_statistics()
        
        text = (
            f"📊 <b>STATISTIKA</b>\n\n"
            f"📅 <b>Bugun:</b>\n"
            f"├ Buyurtmalar: {stats['today_count']}\n"
            f"└ Summa: {stats['today_amount']:,} so'm\n\n"
            f"📈 <b>Jami:</b>\n"
            f"├ Buyurtmalar: {stats['total_count']}\n"
            f"└ Summa: {stats['total_amount']:,} so'm"
        )
        
        await message.answer(text, parse_mode="HTML")
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        await message.answer(f"❌ Xatolik: {e}")

@router.message(F.text == "⏳ Kutayotganlar")
async def pending_orders(message: Message):
    """Kutayotgan buyurtmalar"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
    from database import get_pending_orders
    orders = await get_pending_orders()
    
    if not orders:
        await message.answer("📭 <b>Kutayotgan buyurtmalar yo'q</b>", parse_mode="HTML")
        return
    
    text = "⏳ <b>KUTAYOTGAN BUYURTMALAR:</b>\n\n"
    
    for order in orders:
        order_number = order[1]
        diamonds = order[3]
        price = order[4]
        player_id = order[5]
        
        text += (
            f"📋 #{order_number}\n"
            f"💎 {diamonds} Almaz\n"
            f"💰 {price:,} so'm\n"
            f"🆔 {player_id}\n"
            f"─────────────\n"
        )
    
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "✅ Bajarilganlar")
async def completed_orders_list(message: Message):
    """Bajarilgan buyurtmalar"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
    from database import get_completed_orders
    orders = await get_completed_orders()
    
    if not orders:
        await message.answer("📭 <b>Bajarilgan buyurtmalar yo'q</b>", parse_mode="HTML")
        return
    
    text = "✅ <b>BAJARILGAN BUYURTMALAR:</b>\n\n"
    
    for order in orders[:20]:
        order_number = order[1]
        diamonds = order[3]
        price = order[4]
        player_id = order[5]
        completed_at = order[10]
        
        text += (
            f"📋 #{order_number}\n"
            f"💎 {diamonds} Almaz\n"
            f"💰 {price:,} so'm\n"
            f"🆔 {player_id}\n"
            f"✅ {completed_at}\n"
            f"─────────────\n"
        )
    
    if len(orders) > 20:
        text += f"\n📝 Va yana {len(orders) - 20} ta..."
    
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "📦 Buyurtmalar")
async def all_orders(message: Message):
    """Barcha buyurtmalar"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
    from database import get_all_orders
    orders = await get_all_orders()
    
    if not orders:
        await message.answer("📭 <b>Hali buyurtmalar yo'q</b>", parse_mode="HTML")
        return
    
    text = "📦 <b>BARCHA BUYURTMALAR:</b>\n\n"
    
    for order in orders:
        order_number = order[1]
        user_id = order[2]
        diamonds = order[3]
        price = order[4]
        status = order[8]
        created_at = order[9]
        
        from database import get_user
        user = await get_user(user_id)
        username = f"@{user[1]}" if user and user[1] else "username_yoq"
        
        if status == 'completed':
            status_emoji = '✅'
        elif status == 'payment_confirmed':
            status_emoji = '⏳'
        elif status == 'screenshot_sent':
            status_emoji = '🔍'
        elif status == 'cancelled':
            status_emoji = '❌'
        else:
            status_emoji = '⏳'
        
        text += (
            f"{status_emoji} <b>#{order_number}</b> - {username}\n"
            f"💎 {diamonds} Diamonds - 💰 {price:,} so'm\n"
            f"📅 {created_at[:16]}\n"
            f"─────────────\n"
        )
    
    if len(orders) == 50:
        text += "\n📝 So'ngi 50 ta ko'rsatildi"
    
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "👥 Foydalanuvchilar")
async def users_count(message: Message):
    """Foydalanuvchilar"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
    import aiosqlite
    from config import DB_NAME
    
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        count = (await cursor.fetchone())[0]
    
    await message.answer(
        f"👥 <b>Foydalanuvchilar:</b> {count} ta",
        parse_mode="HTML"
    )

@router.message(F.text == "⚙️ Sozlamalar")
async def settings(message: Message):
    """Sozlamalar"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
    from keyboards import settings_menu
    await message.answer(
        "⚙️ <b>SOZLAMALAR</b>\n\n"
        "Qaysi sozlamani o'zgartirmoqchisiz?",
        reply_markup=settings_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "settings_prices")
async def show_prices_settings(callback: CallbackQuery):
    """Narxlar sozlamalari"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Sizda ruxsat yo'q!")
        return
    
    from database import get_all_packages
    from keyboards import package_list_keyboard
    
    packages = await get_all_packages()
    
    await callback.message.edit_text(
        "💰 <b>PAKET NARXLARI</b>\n\n"
        "O'zgartirmoqchi bo'lgan paketni tanlang:",
        reply_markup=package_list_keyboard(packages),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "settings_payment")
async def show_payment_settings(callback: CallbackQuery):
    """To'lov ma'lumoti sozlamalari"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Sizda ruxsat yo'q!")
        return
    
    from database import get_payment_info
    from keyboards import payment_edit_keyboard
    
    payment = await get_payment_info()
    
    await callback.message.edit_text(
        "💳 <b>TO'LOV MA'LUMOTI</b>\n\n"
        f"💳 Karta: <code>{payment['card']}</code>\n"
        f"📱 Telefon: <code>{payment['phone']}</code>\n"
        f"👤 Ism: {payment['name']}\n\n"
        "O'zgartirmoqchi bo'lgan ma'lumotni tanlang:",
        reply_markup=payment_edit_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "settings_texts")
async def show_texts_settings(callback: CallbackQuery):
    """Matnlar sozlamalari"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Sizda ruxsat yo'q!")
        return
    
    from keyboards import texts_edit_keyboard
    
    await callback.message.edit_text(
        "📝 <b>BOT MATNLARI</b>\n\n"
        "O'zgartirmoqchi bo'lgan matnni tanlang:",
        reply_markup=texts_edit_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "settings_menu")
async def back_to_settings(callback: CallbackQuery):
    """Sozlamalarga qaytish"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Sizda ruxsat yo'q!")
        return
    
    from keyboards import settings_menu
    await callback.message.edit_text(
        "⚙️ <b>SOZLAMALAR</b>\n\n"
        "Qaysi sozlamani o'zgartirmoqchisiz?",
        reply_markup=settings_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "settings_back")
async def close_settings(callback: CallbackQuery):
    """Sozlamalarni yopish"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Sizda ruxsat yo'q!")
        return
    
    await callback.message.delete()
    await callback.answer()

@router.callback_query(F.data.startswith("edit_price_"))
async def edit_package_price(callback: CallbackQuery, state: FSMContext):
    """Paket narxini o'zgartirish"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Sizda ruxsat yo'q!")
        return
    
    await callback.message.edit_text(
        "💰 <b>NARXNI O'ZGARTIRISH</b>\n\n"
        "⚠️ Bu funksiya keyingi versiyada qo'shiladi.\n\n"
        "Hozircha narxlarni <code>config.py</code> faylidan o'zgartiring.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings_prices")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("edit_"))
async def edit_payment_field(callback: CallbackQuery):
    """To'lov ma'lumotini o'zgartirish"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Sizda ruxsat yo'q!")
        return
    
    field = callback.data.replace("edit_", "")
    
    if field == "card":
        field_name = "karta raqami"
    elif field == "phone":
        field_name = "telefon"
    elif field == "name":
        field_name = "ism"
    elif field == "welcome":
        field_name = "xush kelibsiz matni"
    elif field == "payment_text":
        field_name = "to'lov matni"
    else:
        field_name = "ma'lumot"
    
    await callback.message.edit_text(
        f"📝 <b>{field_name.upper()} O'ZGARTIRISH</b>\n\n"
        f"⚠️ Bu funksiya keyingi versiyada qo'shiladi.\n\n"
        f"Hozircha {field_name}ni <code>config.py</code> faylidan o'zgartiring.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings_payment" if field in ["card", "phone", "name"] else "settings_texts")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(F.photo)
async def get_photo_id(message: Message):
    """Photo ID olish (vaqtinchalik)"""
    if message.from_user.id in ADMIN_IDS:
        file_id = message.photo[-1].file_id
        await message.answer(f"File ID: <code>{file_id}</code>", parse_mode="HTML")