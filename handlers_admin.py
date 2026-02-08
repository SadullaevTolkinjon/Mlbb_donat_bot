from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from config import ADMIN_IDS
from database import (
    confirm_payment, 
    complete_order, 
    get_order, 
    get_statistics, 
    cancel_order, 
    get_order_by_number,
    get_admin_notifications  # ✅ QOSHILDI
)

router = Router()


@router.callback_query(F.data.startswith("admin_confirm_"))
async def confirm_payment_callback(callback: CallbackQuery, bot):
    """To'lovni tasdiqlash - EDIT MESSAGE (yangi message emas!)"""
    
    # DARHOL ANSWER (loading icon yo'qoladi)
    await callback.answer("✅ Tasdiqlanyapti...", show_alert=False)
    
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Sizda ruxsat yo'q!", show_alert=True)
        return
    
    order_number = callback.data.replace("admin_confirm_", "")
    print(f"✅ Admin {callback.from_user.username} confirming order: {order_number}")
    
    # Statusni yangilash
    await confirm_payment(order_number)
    
    # Buyurtma ma'lumotlarini olish
    order = await get_order_by_number(order_number)
    
    if not order:
        await callback.answer("❌ Buyurtma topilmadi!", show_alert=True)
        return
    
    user_id = order[2]
    diamonds = order[3]
    price = order[4]
    player_id = order[5]
    zone_id = order[6]
    
    # Yangilangan caption
    updated_caption = (
        f"✅ <b>TO'LOV TASDIQLANDI</b>\n\n"
        f"📋 <b>Buyurtma:</b> #{order_number}\n"
        f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
        f"💎 <b>Paket:</b> {diamonds} Almaz\n"
        f"💰 <b>Summa:</b> {price:,} so'm\n"
        f"🎮 <b>ID:</b> <code>{player_id} ({zone_id})</code>\n\n"
        f"👤 <b>Admin:</b> @{callback.from_user.username or 'admin'}\n"
        f"✅ <b>To'lov tasdiqlandi!</b>\n\n"
        f"📸 <b>Screenshot:</b>"
    )
    
    # ✅ BARCHA ADMINLARDA EDIT QILISH
    from keyboards import delivery_keyboard
    
    admin_messages = await get_admin_notifications(order_number)
    print(f"✅ Found {len(admin_messages)} admin messages to edit")
    
    for admin_id, message_id in admin_messages.items():
        try:
            await bot.edit_message_caption(
                chat_id=admin_id,
                message_id=message_id,
                caption=updated_caption,
                parse_mode="HTML",
                reply_markup=delivery_keyboard(order_number)
            )
            print(f"✅ Edited message for admin {admin_id}")
        except Exception as e:
            print(f"❌ Admin {admin_id} edit error: {e}")
    
    # User ga xabar
    try:
        await bot.send_message(
            user_id,
            f"✅ <b>TO'LOVINGIZ TASDIQLANDI!</b>\n\n"
            f"📋 Buyurtma: <code>#{order_number}</code>\n"
            f"💎 {diamonds} Almaz\n\n"
            f"⏳ Adminlar 💎 yubormoqda...\n"
            f"📱 5-10 daqiqada hisobingizga tushadi!",
            parse_mode="HTML"
        )
        print(f"✅ Notification sent to user {user_id}")
    except Exception as e:
        print(f"❌ User notification error: {e}")


@router.callback_query(F.data.startswith("admin_complete_"))
async def admin_complete_order(callback: CallbackQuery, bot):
    """Admin almaz yuborildi - EDIT MESSAGE"""
    
    # DARHOL ANSWER
    await callback.answer("✅ Bajarildi!", show_alert=False)
    
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Sizda ruxsat yo'q!", show_alert=True)
        return
    
    order_number = callback.data.replace("admin_complete_", "")
    print(f"💎 Admin {callback.from_user.username} completing order: {order_number}")
    
    # Buyurtmani yakunlash
    await complete_order(order_number)
    
    # Buyurtma ma'lumotlarini olish
    order = await get_order_by_number(order_number)
    
    if not order:
        await callback.answer("❌ Buyurtma topilmadi!", show_alert=True)
        return
    
    user_id = order[2]
    diamonds = order[3]
    price = order[4]
    player_id = order[5]
    zone_id = order[6]
    
    # Yangilangan caption
    updated_caption = (
        f"✅ <b>BUYURTMA BAJARILDI</b>\n\n"
        f"📋 <b>Buyurtma:</b> #{order_number}\n"
        f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
        f"💎 <b>Paket:</b> {diamonds} Almaz\n"
        f"💰 <b>Summa:</b> {price:,} so'm\n"
        f"🎮 <b>ID:</b> <code>{player_id} ({zone_id})</code>\n\n"
        f"👤 <b>Yubordi:</b> @{callback.from_user.username or 'admin'}\n"
        f"💎 <b>Yuborildi!</b>\n\n"
        f"📸 <b>Screenshot:</b>"
    )
    
    # ✅ BARCHA ADMINLARDA EDIT QILISH (tugmalarni o'chirish)
    admin_messages = await get_admin_notifications(order_number)
    
    for admin_id, message_id in admin_messages.items():
        try:
            await bot.edit_message_caption(
                chat_id=admin_id,
                message_id=message_id,
                caption=updated_caption,
                parse_mode="HTML",
                reply_markup=None  # Tugmalarni o'chirish
            )
            print(f"✅ Completed message edited for admin {admin_id}")
        except Exception as e:
            print(f"❌ Admin {admin_id} edit error: {e}")
    
    # Userga xabar
    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"🎉 <b>BUYURTMA BAJARILDI!</b>\n\n"
                f"📋 Buyurtma: <code>#{order_number}</code>\n"
                f"💎 {diamonds} Almaz yuborildi!\n\n"
                f"🎮 Hisobingizni tekshiring!\n"
                f"⭐️ Rahmat, yana buyurtma bering!"
            ),
            parse_mode="HTML"
        )
        print(f"✅ Completion message sent to user {user_id}")
    except Exception as e:
        print(f"❌ User message error: {e}")


@router.callback_query(F.data.startswith("admin_cancel_"))
async def admin_cancel_order(callback: CallbackQuery, bot):
    """Admin buyurtmani bekor qiladi - EDIT MESSAGE"""
    
    # DARHOL ANSWER
    await callback.answer("❌ Bekor qilinyapti...", show_alert=False)
    
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Sizda ruxsat yo'q!", show_alert=True)
        return
    
    order_number = callback.data.replace("admin_cancel_", "")
    print(f"❌ Admin {callback.from_user.username} cancelling order: {order_number}")
    
    # Statusni yangilash
    await cancel_order(order_number)
    
    # Buyurtma ma'lumotlarini olish
    order = await get_order_by_number(order_number)
    
    if not order:
        await callback.answer("❌ Buyurtma topilmadi!", show_alert=True)
        return
    
    user_id = order[2]
    diamonds = order[3]
    price = order[4]
    player_id = order[5]
    zone_id = order[6]
    
    # Yangilangan caption
    updated_caption = (
        f"❌ <b>BUYURTMA BEKOR QILINDI</b>\n\n"
        f"📋 <b>Buyurtma:</b> #{order_number}\n"
        f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
        f"💎 <b>Paket:</b> {diamonds} Almaz\n"
        f"💰 <b>Summa:</b> {price:,} so'm\n"
        f"🎮 <b>ID:</b> <code>{player_id} ({zone_id})</code>\n\n"
        f"👤 <b>Bekor qildi:</b> @{callback.from_user.username or 'admin'}\n"
        f"❌ <b>Rad etildi!</b>\n\n"
        f"📸 <b>Screenshot:</b>"
    )
    
    # ✅ BARCHA ADMINLARDA EDIT QILISH
    admin_messages = await get_admin_notifications(order_number)
    
    for admin_id, message_id in admin_messages.items():
        try:
            await bot.edit_message_caption(
                chat_id=admin_id,
                message_id=message_id,
                caption=updated_caption,
                parse_mode="HTML",
                reply_markup=None
            )
            print(f"✅ Cancelled message edited for admin {admin_id}")
        except Exception as e:
            print(f"❌ Admin {admin_id} edit error: {e}")
    
    # Userga xabar
    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"❌ <b>BUYURTMA BEKOR QILINDI</b>\n\n"
                f"📋 Buyurtma: <code>#{order_number}</code>\n"
                f"💎 {diamonds} Almaz\n\n"
                f"Iltimos qaytadan urinib ko'ring yoki "
                f"admin bilan bog'laning:\n"
                f"👨‍💼 @Retriccodonat"
            ),
            parse_mode="HTML"
        )
        print(f"✅ Cancel message sent to user {user_id}")
    except Exception as e:
        print(f"❌ User message error: {e}")


@router.message(Command("stats"))
async def show_statistics(message: Message):
    """Statistika (faqat admin)"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
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