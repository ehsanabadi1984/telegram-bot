from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz  # اضافه کردن pytz برای تنظیم منطقه زمانی
import mimetypes
# استفاده از منطقه زمانی مناسب
scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Tehran'))
scheduler.start()

TOKEN = "8007267423:AAEQR9MJDbaEeNWPBRDON7hKKAbdvUDRyDM"

# مرحله اول: کاربر با /start شروع می‌کنه
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("سلام! لطفاً یه فایل بفرست و بعد بهم بگو چه اسمی براش بذارم.")

# ذخیره فایل و درخواست نام جدید
async def handle_file(update: Update, context: CallbackContext):
    file = update.message.document or update.message.video or update.message.audio or (update.message.photo[-1] if update.message.photo else None)

    if not file:
        await update.message.reply_text("فایل نامعتبره.")
        return

    file_id = file.file_id
    context.user_data['file_id'] = file_id

    # گرفتن مسیر فایل و استخراج فرمت واقعی
    tg_file = await context.bot.get_file(file_id)
    file_path = tg_file.file_path
    extension = os.path.splitext(file_path)[-1]  # مثل .jpg یا .mp4

    if not extension:
        # اگر فایل فرمت نداشت
        extension = mimetypes.guess_extension(getattr(file, 'mime_type', '') or '') or '.dat'

    context.user_data['extension'] = extension
    await update.message.reply_text("فایل دریافت شد ✅ لطفاً اسم جدید فایل رو بفرست (بدون فرمت).")
async def handle_text(update: Update, context: CallbackContext):
    if 'file_id' in context.user_data:
        file_id = context.user_data['file_id']
        extension = context.user_data.get('extension', '.dat')

        file = await context.bot.get_file(file_id)
        new_name = update.message.text
        full_name = f"{new_name}{extension}"

        await file.download_to_drive(full_name)
        await update.message.reply_document(open(full_name, 'rb'))
        os.remove(full_name)
        context.user_data.clear()
    else:
        await update.message.reply_text("اول باید یه فایل بفرستی.")

# راه‌اندازی ربات
async def main():
    # ایجاد اپلیکیشن و ربات
    application = Application.builder().token(TOKEN).build()

    # افزودن handler ها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ATTACHMENT, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # شروع کردن ربات
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    import nest_asyncio
    nest_asyncio.apply()

    try:
        asyncio.run(main())
    except RuntimeError as e:
        print("خطای event loop:", e)
