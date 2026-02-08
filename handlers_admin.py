from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from config import ADMIN_IDS
from database import confirm_payment, complete_order, get_order, get_statistics, cancel_order, get_order_by_number

router = Router()

@router.callback_query(F.data.startswith("confirm_"))
async def confirm_payment_callback(callback: CallbackQuery, bot):
    """To'lovni tasdiqlash"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Sizda ruxsat yo'q!")
        return
    
    order_number = callback.data.replace("confirm_", "")
    
    # Statusni yangilash
    await confirm_payment(order_number)
    
    # Buyurtma ma'lumotlarini olish
    order = await get_order_by_number(order_number)
    
    if not order:
        await callback.answer("❌ Buyurtma topilmadi!")
        return
    
    user_id = order[2]
    screenshot_id = order[7]
    
    # Yangilangan caption
    updated_caption = (
        f"{callback.message.caption}\n\n"
        f"✅ To'lov tasdiqlandi!\n"
        f"👤 Admin: @{callback.from_user.username or 'admin'}"
    )
    
    # BARCHA adminlarga yangilangan xabar yuborish
    from keyboards import delivery_keyboard
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_photo(
                chat_id=admin_id,
                photo=screenshot_id,
                caption=updated_caption,
                reply_markup=delivery_keyboard(order_number),
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"❌ Admin {admin_id} ga yangilanish yuborilmadi: {e}")
    
    # User ga xabar
    try:
        await bot.send_message(
            user_id,
            f"✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
            f"📋 Buyurtma: #{order_number}\n"
            f"⏳ Tez orada almaz yuboriladi!",
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"❌ User ga xabar yuborilmadi: {e}")
    
    # Hozirgi admin uchun eski xabarni yangilash
    try:
        await callback.message.edit_caption(
            caption=updated_caption,
            reply_markup=delivery_keyboard(order_number)
        )
    except:
        pass  # Agar edit qilib bo'lmasa, skip
    
    await callback.answer("✅ To'lov tasdiqlandi!")

@router.callback_query(F.data.startswith("admin_complete_"))
async def admin_complete_order(callback: CallbackQuery, bot):
    """Admin almaz yuborildi deb belgilaydi"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Sizda ruxsat yo'q!")
        return
    
    order_number = callback.data.replace("admin_complete_", "")
    
    print(f"💎 Admin completing order: {order_number}")
    
    # Buyurtmani yakunlash
    await complete_order(order_number)
    
    # Buyurtma ma'lumotlarini olish
    order = await get_order(order_number)
    
    if not order:
        await callback.answer("❌ Buyurtma topilmadi!")
        return
    
    user_id = order[2]
    diamonds = order[3]
    screenshot_id = order[7]
    
    # Yangilangan caption
    updated_caption = (
        f"{callback.message.caption}\n\n"
        f"💎 Yuborildi!\n"
        f"👤 Admin: @{callback.from_user.username or 'admin'}"
    )
    
    # BARCHA adminlarga yangilangan xabar yuborish
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_photo(
                chat_id=admin_id,
                photo=screenshot_id,
                caption=updated_caption,
                reply_markup=None,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"❌ Admin {admin_id} ga yangilanish yuborilmadi: {e}")
    
    # Userga xabar
    print(f"💎 Sending completion message to user: {user_id}")
    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"🎉 <b>BAJARILDI!</b>\n\n"
                f"📋 Buyurtma: #{order_number}\n"
                f"💎 {diamonds} Almaz yuborildi!\n\n"
                f"O'yiningizni tekshiring! ✅\n"
                f"Rahmat! 🙏"
            ),
            parse_mode="HTML"
        )
        print("✅ Completion message sent successfully!")
    except Exception as e:
        print(f"❌ Error sending completion message: {e}")
    
    # Hozirgi admin uchun eski xabarni yangilash
    try:
        await callback.message.edit_caption(
            caption=updated_caption,
            reply_markup=None,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"❌ Error editing caption: {e}")
    
    await callback.answer("🎉 Bajarildi!")

@router.callback_query(F.data.startswith("admin_cancel_"))
async def admin_cancel_order(callback: CallbackQuery, bot):
    """Admin buyurtmani bekor qiladi"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Sizda ruxsat yo'q!")
        return
    
    order_number = callback.data.replace("admin_cancel_", "")
    
    # Statusni yangilash
    await cancel_order(order_number)
    
    # Buyurtma ma'lumotlarini olish
    order = await get_order(order_number)
    
    if not order:
        await callback.answer("❌ Buyurtma topilmadi!")
        return
    
    user_id = order[2]
    screenshot_id = order[7]
    
    # Yangilangan caption
    updated_caption = (
        f"{callback.message.caption}\n\n"
        f"❌ Bekor qilindi!\n"
        f"👤 Admin: @{callback.from_user.username or 'admin'}"
    )
    
    # BARCHA adminlarga yangilangan xabar yuborish
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_photo(
                chat_id=admin_id,
                photo=screenshot_id,
                caption=updated_caption,
                reply_markup=None,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"❌ Admin {admin_id} ga yangilanish yuborilmadi: {e}")
    
    # Userga xabar
    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"❌ <b>Buyurtma bekor qilindi</b>\n\n"
                f"📋 Buyurtma: #{order_number}\n\n"
                f"Iltimos qaytadan urinib ko'ring yoki "
                f"admin bilan bog'laning: @Retriccodonat"
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"❌ Error sending cancel message: {e}")
    
    # Hozirgi admin uchun eski xabarni yangilash
    try:
        await callback.message.edit_caption(
            caption=updated_caption,
            reply_markup=None,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"❌ Error editing caption: {e}")
    
    await callback.answer("❌ Bekor qilindi!")

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