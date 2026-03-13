import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
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

# Данные пользователей
user_data = {}

# Рамки для профиля
TOP = "╔═════════════════╗"
TITLE = "║         👤  ПРОФИЛЬ          ║"
MID = "╠═════════════════╣"
BOT = "╚═════════════════╝"
EMPTY = "║                 ║"

def make_profile(user_id):
    data = user_data.get(user_id, {})
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

def start(update, context):
    user_id = update.effective_user.id
    user_data[user_id] = {
        'name': '', 'age': '', 'hobby': '', 'contact': '', 
        'best_friend': '', 'channel': 'нету', 'custom': '',
        'username': update.effective_user.username or 'нет'
    }
    update.message.reply_text("🌟 **Создание профиля** 🌟\n\nДля начала, напиши свое **Имя**:", parse_mode='Markdown')
    return NAME

def get_name(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['name'] = update.message.text
    update.message.reply_text("✅ Имя сохранено!\n\nТеперь напиши свой **Возраст**:", parse_mode='Markdown')
    return AGE

def get_age(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['age'] = update.message.text
    update.message.reply_text("✅ Возраст сохранен!\n\nРасскажи о своем **Хобби**:", parse_mode='Markdown')
    return HOBBY

def get_hobby(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['hobby'] = update.message.text
    update.message.reply_text("✅ Хобби сохранено!\n\nУкажи **Контакт** для связи:", parse_mode='Markdown')
    return CONTACT

def get_contact(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['contact'] = update.message.text
    update.message.reply_text("✅ Контакт сохранен!\n\nКто твой **Best friend**?", parse_mode='Markdown')
    return BEST_FRIEND

def get_best_friend(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['best_friend'] = update.message.text
    
    keyboard = [[
        InlineKeyboardButton("✅ Указать канал", callback_data='add_channel'),
        InlineKeyboardButton("⏭️ Пропустить", callback_data='skip_channel')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text("Хочешь указать канал?", reply_markup=reply_markup)
    return CHANNEL

def channel_callback(update, context):
    query = update.callback_query
    query.answer()
    
    if query.data == 'skip_channel':
        show_profile(update, context)
        return ConversationHandler.END
    else:
        query.edit_message_text("Напиши название канала:")
        return CHANNEL

def get_channel(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['channel'] = update.message.text
    show_profile(update, context)
    return ConversationHandler.END

def show_profile(update, context):
    user_id = update.effective_user.id
    
    keyboard = [[
        InlineKeyboardButton("➕ Добавить строку", callback_data='add_custom'),
        InlineKeyboardButton("🔄 Обновить", callback_data='refresh')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = make_profile(user_id)
    
    if hasattr(update, 'callback_query'):
        update.callback_query.edit_message_text(
            text=f"```\n{text}\n```",
            parse_mode='MarkdownV2',
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text(
            text=f"```\n{text}\n```",
            parse_mode='MarkdownV2',
            reply_markup=reply_markup
        )

def button_handler(update, context):
    query = update.callback_query
    query.answer()
    
    if query.data == 'refresh':
        show_profile(update, context)
    elif query.data == 'add_custom':
        query.edit_message_text("Введите текст для новой строки:")
        return CUSTOM

def get_custom(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['custom'] = update.message.text
    show_profile(update, context)
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text('❌ Отменено. Начните заново с /start')
    return ConversationHandler.END

def main():
    # СОЗДАЕМ UPDATER (для старых версий библиотеки)
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            AGE: [MessageHandler(Filters.text & ~Filters.command, get_age)],
            HOBBY: [MessageHandler(Filters.text & ~Filters.command, get_hobby)],
            CONTACT: [MessageHandler(Filters.text & ~Filters.command, get_contact)],
            BEST_FRIEND: [MessageHandler(Filters.text & ~Filters.command, get_best_friend)],
            CHANNEL: [
                CallbackQueryHandler(channel_callback, pattern='^(add_channel|skip_channel)$'),
                MessageHandler(Filters.text & ~Filters.command, get_channel)
            ],
            CUSTOM: [MessageHandler(Filters.text & ~Filters.command, get_custom)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(button_handler, pattern='^(add_custom|refresh)$'))
    
    print("✅ БОТ ЗАПУЩЕН НА СТАРОЙ ВЕРСИИ!")
    
    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
