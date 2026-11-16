import logging
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes, MessageHandler, filters
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.environ["BOT_TOKEN"]
PORT = int(os.environ.get("PORT", "10000"))
RENDER_EXTERNAL_URL = os.environ["RENDER_EXTERNAL_URL"].rstrip("/")

MENU = ReplyKeyboardMarkup(
    [["📊 Bosqichlar bo‘yicha", "🎯 Koeffitsiyent bo‘yicha"],
     ["ℹ️ Yordam"]],
    resize_keyboard=True,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Salom! Men Chicken Road 2 uchun matematik ehtimollik kalkulyatoriman.\n\n"
        "Men keyingi yurishni bashorat qilmayman va o‘yin serveriga ulanmayman. "
        "Faqat siz kiritgan raqamlar asosida hisoblayman.\n\n"
        "Kerakli hisob turini tanlang:",
        reply_markup=MENU,
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Hisob bekor qilindi. Menyudan tanlang:", reply_markup=MENU)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Bosqichlar bo‘yicha: bitta bosqichdan omon o‘tish ehtimoli (%) "
        "va bosqichlar sonini kiritasiz. Bot umumiy ehtimolni hisoblaydi.\n\n"
        "🎯 Koeffitsiyent bo‘yicha: jami to‘lov koeffitsiyentini (stavka ham ichida) "
        "va RTP foizini kiritasiz. Soddalashtirilgan model: ehtimol = RTP / koeffitsiyent.\n\n"
        "Bu bashorat yoki yutuq kafolati emas. /cancel — bekor qilish."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    if msg == "ℹ️ Yordam":
        await help_command(update, context)
        return
    if msg == "📊 Bosqichlar bo‘yicha":
        context.user_data.clear()
        context.user_data["mode"] = "stage_rate"
        await update.message.reply_text(
            "Bitta bosqichdan muvaffaqiyatli o‘tish ehtimolini foizda kiriting (masalan, 80):",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    if msg == "🎯 Koeffitsiyent bo‘yicha":
        context.user_data.clear()
        context.user_data["mode"] = "multiplier"
        await update.message.reply_text(
            "Koeffitsiyentni kiriting (masalan, 2.5). Jami qaytim koeffitsiyenti bo‘lishi kerak:",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    mode = context.user_data.get("mode")
    if not mode:
        await update.message.reply_text("Menyudan hisob turini tanlang yoki /start bosing.", reply_markup=MENU)
        return

    try:
        value = float(msg.replace(",", ".").replace("%", "").strip())
    except ValueError:
        await update.message.reply_text("Faqat son kiriting. Masalan: 80 yoki 2.5")
        return

    if mode == "stage_rate":
        if not 0 < value <= 100:
            await update.message.reply_text("Foiz 0 dan katta va 100 dan oshmasligi kerak.")
            return
        context.user_data["p"] = value / 100
        context.user_data["mode"] = "stage_count"
        await update.message.reply_text("Nechta ketma-ket bosqichni hisoblaymiz? (1–100):")
        return

    if mode == "stage_count":
        if not value.is_integer() or not 1 <= value <= 100:
            await update.message.reply_text("1 dan 100 gacha butun son kiriting.")
            return
        p, n = context.user_data["p"], int(value)
        result = (p ** n) * 100
        await update.message.reply_text(
            f"📊 Hisob natijasi\nBitta bosqich: {p*100:.2f}%\n"
            f"Bosqichlar soni: {n}\nKetma-ket muvaffaqiyat ehtimoli: {result:.4f}%\n\n"
            "Bu barcha bosqichlarda ehtimol bir xil va natijalar mustaqil degan farazga asoslanadi. "
            "Bashorat yoki yutuq kafolati emas.",
            reply_markup=MENU,
        )
        context.user_data.clear()
        return

    if mode == "multiplier":
        if value <= 1:
            await update.message.reply_text("Koeffitsiyent 1 dan katta bo‘lsin. Masalan: 2.5")
            return
        context.user_data["multiplier"] = value
        context.user_data["mode"] = "rtp"
        await update.message.reply_text(
            "RTP foizini kiriting (aniq bilmasangiz 100 kiriting; bu tasdiqlangan o‘yin RTPsi degani emas):"
        )
        return

    if mode == "rtp":
        if not 0 < value <= 100:
            await update.message.reply_text("RTP 0 dan katta va 100 dan oshmasligi kerak.")
            return
        m = context.user_data["multiplier"]
        estimate = min(1.0, (value / 100) / m) * 100
        await update.message.reply_text(
            f"🎯 Hisob natijasi\nKoeffitsiyent: {m:g}x\nRTP: {value:g}%\n"
            f"Model bo‘yicha taxminiy ehtimol: {estimate:.4f}%\n\n"
            "Formula: RTP ÷ koeffitsiyent. Bu soddalashtirilgan matematik taxmin; "
            "o‘yin qoidalari va RTP talqini mos kelmasa, haqiqiy ehtimolni bildirmaydi. "
            "Keyingi raundni oldindan aytmaydi.",
            reply_markup=MENU,
        )
        context.user_data.clear()

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Buyruq tushunilmadi. /start ni bosing.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Render Free Web Service uchun webhook rejimi.
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{RENDER_EXTERNAL_URL}/{TOKEN}",
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    main()
