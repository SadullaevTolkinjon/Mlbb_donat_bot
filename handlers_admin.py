from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from config import ADMIN_IDS
from database import confirm_payment, complete_order, get_order, get_statistics

router = Router()

@router.callback_query(F.data.startswith("admin_confirm_"))
async def admin_confirm_payment(callback: CallbackQuery, bot):
    """Admin to'lovni tasdiqlaydi"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Sizda ruxsat yo'q!")
        return
    
    order_number = callback.data.replace("admin_confirm_", "")
    
    print(f"✅ Admin confirming payment: {order_number}")
    
    # Buyurtmani yangilash
    await confirm_payment(order_number)
    
    # Buyurtma ma'lumotlarini olish
    order = await get_order(order_number)
    
    if not order:
        await callback.answer("❌ Buyurtma topilmadi!")
        return
    
    user_id = order[2]  # user_id
    
    print(f"✅ Sending payment confirmed message to user: {user_id}")
    
    # Userga xabar
    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"✅ <b>To'lov tasdiqlandi!</b>\n\n"
                f"📋 Buyurtma: #{order_number}\n"
                f"💎 Almaz 5-10 daqiqada yuboriladi!\n\n"
                f"Iltimos kuting... ⏳"
            ),
            parse_mode="HTML"
        )
        print("✅ Message sent successfully!")
    except Exception as e:
        print(f"❌ Error sending message: {e}")
    
    # Admin xabarini yangilash
    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n✅ <b>TO'LOV TASDIQLANDI</b>",
        reply_markup=callback.message.reply_markup,
        parse_mode="HTML"
    )
    
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
    
    user_id = order[2]  # user_id
    diamonds = order[3]  # diamonds
    
    print(f"💎 Sending completion message to user: {user_id}")
    
    # Userga xabar
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
    
    # Admin xabarini yangilash
    try:
        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n🎉 <b>BAJARILDI!</b>",
            reply_markup=None,  # Tugmalarni olib tashlash
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
    
    # Buyurtma ma'lumotlarini olish
    order = await get_order(order_number)
    
    if not order:
        await callback.answer("❌ Buyurtma topilmadi!")
        return
    
    user_id = order[2]  # user_id
    
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
    
    # Admin xabarini yangilash
    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n❌ <b>BEKOR QILINDI</b>",
        reply_markup=None,
        parse_mode="HTML"
    )
    
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