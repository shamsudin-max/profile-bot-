import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import os
import asyncio

# Включим логирование
logging.basicConfig(
    format='%(asime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен берется из переменных окружения
TOKEN = os.getenv('BOT_TOKEN')

# Состояния для ConversationHandler
(NAME, AGE, HOBBY, CONTACT, BEST_FRIEND, CHANNEL, 
 CUSTOM_FIELD_TITLE, CUSTOM_FIELD_VALUE) = range(8)

# Словарь для хранения данных пользователей
user_data = {}

# Константы для оформления
TOP_BORDER = "╔═════════════════╗"
TITLE_LINE = "║         👤  ПРОФИЛЬ          ║"
MIDDLE_BORDER = "╠═════════════════╣"
BOTTOM_BORDER = "╚═════════════════╝"
EMPTY_LINE = "║                 ║"

def create_profile_text(user_id):
    data = user_data[user_id]
    
    profile_lines = [
        TOP_BORDER,
        TITLE_LINE,
        MIDDLE_BORDER,
        f"║ 📝 Имя: {data['name']}",
        MIDDLE_BORDER,
        f"║ 📅 Возраст: {data['age']}",
        MIDDLE_BORDER,
        f"║ 🆔 Username: @{data['username']}",
        EMPTY_LINE,
        MIDDLE_BORDER,
        f"║ 📢 Канал: {data['channel']}",
        EMPTY_LINE,
        MIDDLE_BORDER,
        f"║ 🎨 Хобби:",
        f"║ {data['hobby']}",
        MIDDLE_BORDER,
        f"║ 📞 Контакт:",
        f"║ {data['contact']}",
        MIDDLE_BORDER,
        f"║ Best friend:",
        f"║ {data['best_friend']}",
    ]
    
    for field in data['custom_fields']:
        profile_lines.append(MIDDLE_BORDER)
        profile_lines.append(f"║ {field['title']}:")
        value_lines = split_text(field['value'], 17)
        for line in value_lines:
            profile_lines.append(f"║ {line}")
        profile_lines.append(EMPTY_LINE)
    
    profile_lines.append(BOTTOM_BORDER)
    return "\n".join(profile_lines)

def split_text(text, max_length):
    if len(text) <= max_length:
        return [text]
    result = []
    for i in range(0, len(text), max_length):
        result.append(text[i:i+max_length])
    return result

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    user_data[user_id] = {
        'name': '',
        'age': '',
        'username': update.effective_user.username or 'Нет username',
        'channel': 'нету',
        'hobby': '',
        'contact': '',
        'best_friend': '',
        'custom_fields': []
    }
    
    await update.message.reply_text(
        "🌟 **Создание профиля** 🌟\n\n"
        "Для начала, напиши свое **Имя**:",
        parse_mode='Markdown'
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['name'] = update.message.text
    await update.message.reply_text("✅ Имя сохранено!\n\nТеперь напиши свой **Возраст**:", parse_mode='Markdown')
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['age'] = update.message.text
    await update.message.reply_text("✅ Возраст сохранен!\n\nРасскажи о своем **Хобби**:", parse_mode='Markdown')
    return HOBBY

async def get_hobby(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['hobby'] = update.message.text
    await update.message.reply_text("✅ Хобби сохранено!\n\nУкажи **Контакт** для связи:", parse_mode='Markdown')
    return CONTACT

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['contact'] = update.message.text
    await update.message.reply_text("✅ Контакт сохранен!\n\nКто твой **Best friend**?", parse_mode='Markdown')
    return BEST_FRIEND

async def get_best_friend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['best_friend'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("✅ Да, указать канал", callback_data='add_channel')],
        [InlineKeyboardButton("⏭️ Пропустить", callback_data='skip_channel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "✅ Best friend сохранен!\n\nХочешь указать свой канал?",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return CHANNEL

async def get_channel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == 'skip_channel':
        user_data[user_id]['channel'] = 'нету'
        await show_final_profile(update, context)
        return ConversationHandler.END
    else:
        await query.edit_message_text("Напиши название или ссылку на канал:")
        return CHANNEL

async def get_channel_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['channel'] = update.message.text
    await show_final_profile(update, context)
    return ConversationHandler.END

async def show_final_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton("✏️ Редактировать имя", callback_data='edit_name')],
        [InlineKeyboardButton("✏️ Редактировать возраст", callback_data='edit_age')],
        [InlineKeyboardButton("✏️ Редактировать хобби", callback_data='edit_hobby')],
        [InlineKeyboardButton("✏️ Редактировать контакт", callback_data='edit_contact')],
        [InlineKeyboardButton("✏️ Редактировать Best friend", callback_data='edit_best_friend')],
        [InlineKeyboardButton("✏️ Редактировать канал", callback_data='edit_channel')],
        [InlineKeyboardButton("➕ ДОБАВИТЬ НОВУЮ СТРОКУ", callback_data='add_field_start')],
        [InlineKeyboardButton("🔄 Обновить профиль", callback_data='refresh')],
        [InlineKeyboardButton("❌ Заполнить заново", callback_data='restart')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    profile_text = create_profile_text(user_id)
    
    # Экранируем специальные символы для MarkdownV2
    profile_text = profile_text.replace('-', '\\-').replace('.', '\\.').replace('!', '\\!')
    
    if hasattr(update, 'callback_query') and update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text=f"```\n{profile_text}\n```",
                parse_mode='MarkdownV2',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error: {e}")
    else:
        try:
            await update.message.reply_text(
                text=f"```\n{profile_text}\n```",
                parse_mode='MarkdownV2',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    action = query.data
    
    if action == 'refresh':
        await show_final_profile(update, context)
    elif action == 'restart':
        if user_id in user_data:
            user_data[user_id] = {
                'name': '',
                'age': '',
                'username': update.effective_user.username or 'Нет username',
                'channel': 'нету',
                'hobby': '',
                'contact': '',
                'best_friend': '',
                'custom_fields': []
            }
        await query.edit_message_text("Начинаем заново!\nНапиши свое имя:")
        return NAME
    elif action.startswith('edit_'):
        field = action.replace('edit_', '')
        context.user_data['editing_field'] = field
        field_names = {'name': 'имя', 'age': 'возраст', 'hobby': 'хобби', 'contact': 'контакт', 'best_friend': 'Best friend', 'channel': 'канал'}
        await query.edit_message_text(f"Введите новое значение для поля '{field_names[field]}':")
    elif action == 'add_field_start':
        context.user_data['editing_field'] = 'new_field_title'
        await query.edit_message_text("Введите НАЗВАНИЕ для новой строки (например: Город, Работа):")
        return CUSTOM_FIELD_TITLE

async def handle_edit_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if 'editing_field' in context.user_data:
        field = context.user_data['editing_field']
        field_mapping = {'name': 'name', 'age': 'age', 'hobby': 'hobby', 'contact': 'contact', 'best_friend': 'best_friend', 'channel': 'channel'}
        
        if field in field_mapping:
            user_data[user_id][field_mapping[field]] = text
            context.user_data['editing_field'] = None
            await show_final_profile(update, context)
    return ConversationHandler.END

async def get_custom_field_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data['new_field_title'] = update.message.text
    await update.message.reply_text(f"Теперь введите ЗНАЧЕНИЕ для поля '{update.message.text}':")
    return CUSTOM_FIELD_VALUE

async def get_custom_field_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    title = context.user_data.get('new_field_title', 'Поле')
    value = update.message.text
    
    user_data[user_id]['custom_fields'].append({'title': title, 'value': value})
    del context.user_data['new_field_title']
    
    await update.message.reply_text(f"✅ Строка '{title}' добавлена!")
    await show_final_profile(update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('❌ Отменено. Начните заново с /start')
    return ConversationHandler.END

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data or not user_data[user_id].get('name'):
        await update.message.reply_text("❌ Профиль не найден!\nСоздайте с /start")
        return
    await show_final_profile(update, context)

def main():
    # ПРОСТОЙ ЗАПУСК - БЕЗ ВСЯКИХ HTTPXRequest!
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            HOBBY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_hobby)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
            BEST_FRIEND: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_best_friend)],
            CHANNEL: [
                CallbackQueryHandler(get_channel_callback, pattern='^(add_channel|skip_channel)$'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_channel_text)
            ],
            CUSTOM_FIELD_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_custom_field_title)],
            CUSTOM_FIELD_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_custom_field_value)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))
    
    application.add_handler(CallbackQueryHandler(button_callback, pattern='^(edit_|refresh|restart|add_field_start)'))
    application.add_handler(CommandHandler('profile', profile))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_text))
    
    print("✅ Бот успешно запущен!")
    print(f"🤖 Токен: {TOKEN[:10]}... (скрыт)")
    print("📝 Используйте /start для создания профиля")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
