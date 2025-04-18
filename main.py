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
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://telegram-bot-production-41ba.up.railway.app{WEBHOOK_PATH}"

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
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ATTACHMENT, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    await application.bot.set_webhook("https://telegram-bot-production-41ba.up.railway.app/webhook")

    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        webhook_path="/webhook",
        allowed_updates=Update.ALL_TYPES,
    )

