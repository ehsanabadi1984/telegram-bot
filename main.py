from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz  # اضافه کردن pytz برای تنظیم منطقه زمانی

# استفاده از منطقه زمانی مناسب
scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Tehran'))
scheduler.start()

TOKEN = "8007267423:AAEQR9MJDbaEeNWPBRDON7hKKAbdvUDRyDM"

# مرحله اول: کاربر با /start شروع می‌کنه
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("سلام! لطفاً یه فایل بفرست و بعد بهم بگو چه اسمی براش بذارم.")

# ذخیره فایل و درخواست نام جدید
async def handle_file(update: Update, context: CallbackContext):
    # چک کردن اینکه فایل از چه نوعی هست
    if update.message.document:
        file = update.message.document
    elif update.message.video:
        file = update.message.video
    elif update.message.audio:
        file = update.message.audio
    elif update.message.photo:
        file = update.message.photo[-1]  # آخرین عکس ارسال شده
    else:
        file = None

    if file:
        print(f"Received file: {file.file_id}")
        file_id = file.file_id
        context.user_data['file_id'] = file_id
        context.user_data['file_type'] = file.mime_type
        await update.message.reply_text("فایل دریافت شد ✅ لطفاً اسم جدید فایل رو بفرست (بدون فرمت).")
    else:
        print("No file received.")
        await update.message.reply_text("فایلی ارسال نکردید.")

# گرفتن نام جدید و ارسال فایل
async def handle_text(update: Update, context: CallbackContext):
    if 'file_id' in context.user_data:
        file_id = context.user_data['file_id']
        file = await context.bot.get_file(file_id)

        new_name = update.message.text
        extension = context.user_data.get('file_type', '').split('/')[-1] or 'dat'
        full_name = f"{new_name}.{extension}"

        await file.download_to_drive(full_name)
        await update.message.reply_document(open(full_name, 'rb'))
        os.remove(full_name)  # پاک کردن فایل موقت

        context.user_data.clear()
    else:
        await update.message.reply_text("اول باید یه فایل بفرستی.")

# راه‌اندازی ربات
async def main():
    # ایجاد اپلیکیشن و ربات
    application = Application.builder().token(TOKEN).build()

    # افزودن handler ها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document | filters._Photo | filters._Video | filters._Audio, handle_file))
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
