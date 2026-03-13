import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import os

# Включим логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен
TOKEN = os.getenv('BOT_TOKEN')

# Состояния
(NAME, AGE, HOBBY, CONTACT, BEST_FRIEND, CHANNEL, CUSTOM) = range(7)

# Данные
user_data = {}

# Рамки
TOP = "╔═════════════════╗"
TITLE = "║         👤  ПРОФИЛЬ          ║"
MID = "╠═════════════════╣"
BOT = "╚═════════════════╝"
EMPTY = "║                 ║"

def make_profile(user_id):
    data = user_data[user_id]
    lines = [
        TOP, TITLE, MID,
        f"║ 📝 Имя: {data.get('name', '')}",
        MID,
        f"║ 📅 Возраст: {data.get('age', '')}",
        MID,
        f"║ 🆔 Username: @{data.get('username', '')}",
        EMPTY,
        MID,
        f"║ 📢 Канал: {data.get('channel', 'нету')}",
        EMPTY,
        MID,
        f"║ 🎨 Хобби:",
        f"║ {data.get('hobby', '')}",
        MID,
        f"║ 📞 Контакт:",
        f"║ {data.get('contact', '')}",
        MID,
        f"║ Best friend:",
        f"║ {data.get('best_friend', '')}",
        MID,
        f"║ Дополнительно:",
        f"║ {data.get('custom', '')}",
        EMPTY,
        BOT
    ]
    return "\n".join(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data[uid] = {
        'name': '', 'age': '', 'hobby': '', 'contact': '', 
        'best_friend': '', 'channel': 'нету', 'custom': '',
        'username': update.effective_user.username or 'нет'
    }
    await update.message.reply_text("Привет! Как тебя зовут?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data[uid]['name'] = update.message.text
    await update.message.reply_text("Сколько тебе лет?")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data[uid]['age'] = update.message.text
    await update.message.reply_text("Какое у тебя хобби?")
    return HOBBY

async def get_hobby(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data[uid]['hobby'] = update.message.text
    await update.message.reply_text("Как с тобой связаться?")
    return CONTACT

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data[uid]['contact'] = update.message.text
    await update.message.reply_text("Кто твой лучший друг?")
    return BEST_FRIEND

async def get_best_friend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data[uid]['best_friend'] = update.message.text
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Указать канал", callback_data='add_channel')],
        [InlineKeyboardButton("⏭️ Пропустить", callback_data='skip_channel')]
    ])
    await update.message.reply_text("Хочешь указать канал?", reply_markup=keyboard)
    return CHANNEL

async def channel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'skip_channel':
        await show_profile(update, context)
        return ConversationHandler.END
    else:
        await query.edit_message_text("Напиши название канала:")
        return CHANNEL

async def get_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data[uid]['channel'] = update.message.text
    await show_profile(update, context)
    return ConversationHandler.END

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Добавить строку", callback_data='add_custom')],
        [InlineKeyboardButton("🔄 Обновить", callback_data='refresh')]
    ])
    
    text = make_profile(uid)
    
    if hasattr(update, 'callback_query'):
        await update.callback_query.edit_message_text(
            text=f"```\n{text}\n```",
            parse_mode='MarkdownV2',
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text(
            text=f"```\n{text}\n```",
            parse_mode='MarkdownV2',
            reply_markup=keyboard
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'refresh':
        await show_profile(update, context)
    elif query.data == 'add_custom':
        await query.edit_message_text("Введите текст для новой строки:")
        return CUSTOM

async def get_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data[uid]['custom'] = update.message.text
    await show_profile(update, context)
    return ConversationHandler.END

def main():
    # МАКСИМАЛЬНО ПРОСТОЙ ЗАПУСК
    app = Application.builder().token(TOKEN).build()
    
    # ConversationHandler
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            HOBBY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_hobby)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
            BEST_FRIEND: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_best_friend)],
            CHANNEL: [
                CallbackQueryHandler(channel_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_channel)
            ],
            CUSTOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_custom)]
        },
        fallbacks=[CommandHandler('cancel', lambda u,c: ConversationHandler.END)]
    )
    
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(button_handler, pattern='^(add_custom|refresh)$'))
    
    print("✅ БОТ ЗАПУЩЕН!")
    app.run_polling()

if __name__ == '__main__':
    main()