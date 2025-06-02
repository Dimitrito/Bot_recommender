from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from config import TELEGRAM_BOT_TOKEN
from sqlalchemy.orm import Session
from db import Session, to_dict
from gpt import request_analysis, get_short_description, get_long_description, is_correct_request
from searching import SmartphoneRecommender
import asyncio
from collections import defaultdict

ATTENTION = 3
user_locks = defaultdict(asyncio.Lock)

result_keyboard = [
    [
        InlineKeyboardButton("Детальніше", callback_data="more_info"),
        InlineKeyboardButton("Знайти схожий", callback_data="similar"),
        InlineKeyboardButton("Інші варіанти", callback_data="another")
    ],
]

more_result_keyboard = [
    [
        InlineKeyboardButton("Знайти схожий", callback_data="similar"),
        InlineKeyboardButton("Інші варіанти", callback_data="another")
    ],
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Вітаємо в нашому онлайн-магазині!\n"
        "Розкажи, який смартфон шукаєш — і я допоможу знайти найкращі варіанти!👇")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lock = user_locks[user_id]

    async with lock:
        text = update.message.text
        correct_request = is_correct_request(text)

        if not correct_request:
            await update.message.reply_text("Будь ласка, опишіть який смартфон ви шукаєте")
            return

        await update.message.reply_text(f"Зачекайте, виконується аналіз...")
        db = Session()
        results = []
        attempt = 0

        try:
            while not results and attempt < ATTENTION:
                params = request_analysis(text)
                recommender = SmartphoneRecommender(db)
                results = recommender.find_similar_to_features(params)
                attempt += 1

                if not results:
                    await update.message.reply_text("Виникла помилка, спробуйте ще раз")
                else:
                    context.user_data['number'] = 0
                    context.user_data['results'] = results
                    context.user_data['text'] = text

                    description = get_short_description(text, to_dict(results[0]))
                    reply_markup = InlineKeyboardMarkup(result_keyboard)
                    await update.message.reply_text(description, reply_markup=reply_markup)
        except Exception as e:
            await update.message.reply_text("Виникла помилка, спробуйте ще раз")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lock = user_locks[user_id]

    async with lock:
        try:
            if query.data == "similar":
                await query.message.reply_text("Обробка...")
                number = context.user_data['number']
                results = context.user_data['results']
                text = context.user_data['text']
                db = Session()

                recommender = SmartphoneRecommender(db)
                results = recommender.find_similar(results[number][0].id)

                description = get_short_description(text, to_dict(results[number]))
                reply_markup = InlineKeyboardMarkup(result_keyboard)

                await query.message.reply_text("Схожий варінат\n" + description, reply_markup=reply_markup)

            elif query.data == "more_info":
                await query.message.reply_text("Обробка...")
                number = context.user_data['number']
                results = context.user_data['results']
                text = context.user_data['text']

                description = get_long_description(text, to_dict(results[number]))
                reply_markup = InlineKeyboardMarkup(more_result_keyboard)

                await query.message.reply_text(description, reply_markup=reply_markup)

            elif query.data == "another":
                await query.message.reply_text("Обробка...")
                context.user_data['number'] = context.user_data['number'] + 1

                if context.user_data['number'] >= 5:
                    context.user_data['number'] = 0

                number = context.user_data['number']
                results = context.user_data['results']
                text = context.user_data['text']

                description = get_short_description(text, to_dict(results[number]))
                reply_markup = InlineKeyboardMarkup(result_keyboard)

                await query.message.reply_text("Інший варіант:\n" + description, reply_markup=reply_markup)
        except Exception as e:
            await update.message.reply_text("Виникла помилка, спробуйте ще раз")


def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Бот запущено")
    app.run_polling()
