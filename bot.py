from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

# === Мультиязычность ===
def detect_language(code):
    return code if code in ["ru", "pl"] else "ru"

TRANSLATION_TABLE = {
    "ru": {
        "schab wieprzowy": "свинной карбонат",
        "jogurt naturalny": "йогурт",
    },
    "pl": {
        "свинной карбонат": "schab wieprzowy",
        "йогурт": "jogurt naturalny",
    }
}

def translate_for_search(product, lang):
    return TRANSLATION_TABLE["pl"].get(product.lower(), product)

def display_original(product, lang):
    return TRANSLATION_TABLE["ru"].get(product.lower(), product) if lang == "pl" else product

# === Состояния ===
ENTERING_LIST = 1

# === Главное меню ===
main_menu = ReplyKeyboardMarkup(
    [["📝 Напиши список", "🔍 Поиск скидок по списку"]],
    resize_keyboard=True
)

list_actions = ReplyKeyboardMarkup(
    [["🔍 Найти скидки", "✏️ Изменить список"], ["🧹 Очистить список", "🔙 Назад"]],
    resize_keyboard=True
)

# === Команды ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = detect_language(update.effective_user.language_code)
    context.user_data["lang"] = lang
    await update.message.reply_text(
        "Привет! Что ты хочешь сделать?" if lang == "ru" else "Cześć! Co chcesz zrobić?",
        reply_markup=main_menu
    )

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📝 Напиши список":
        await update.message.reply_text("Отправь список продуктов одним сообщением.")
        return ENTERING_LIST
    elif text == "🔍 Поиск скидок по списку":
        product_list = context.user_data.get("product_list", "")
        if not product_list:
            await update.message.reply_text("Сначала введи список продуктов.")
            return ConversationHandler.END
        lang = context.user_data.get("lang", "ru")
        lines = product_list.split("\n")
        results = []
        for line in lines:
            name = line.split("–")[0].strip()
            translated = translate_for_search(name, lang)
            # Заглушка: имитация поиска
            price = "17.99 zł" if translated == "schab wieprzowy" else "2.99 zł"
            store = "Leclerc"
            original = display_original(translated, lang)
            results.append(f"✅ {original} — {price} ({store})")
        await update.message.reply_text("\n".join(results))
        return ConversationHandler.END

async def receive_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["product_list"] = update.message.text
    await update.message.reply_text("✅ Список сохранён!", reply_markup=list_actions)
    return ConversationHandler.END

# === Запуск ===
app = ApplicationBuilder().token("8390475589:AAENaQ48Dn8cqrza_jY76_2ojXwIkdy8cyY").build()

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)],
    states={
        ENTERING_LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_list)]
    },
    fallbacks=[]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(conv_handler)

app.run_polling()
