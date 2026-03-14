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

# Токен (твой)
TOKEN = '8755447855:AAEH0FyQbDcVIzQ5ad0E7bkeYLPqoARaF64'

# Прокси (рабочий)
PROXY = 'socks5://167.99.233.33:1080'

# Состояния
(NAME, AGE, HOBBY, CONTACT, BEST_FRIEND, CHANNEL, 
 CUSTOM_FIELD_TITLE, CUSTOM_FIELD_VALUE) = range(8)

# Данные пользователей
user_data = {}

# КОНСТАНТЫ ДЛЯ ОФОРМЛЕНИЯ - ТОЧНО КАК В ПРИМЕРЕ
TOP_BORDER = "╔═════════════════╗"
TITLE_LINE = "║         👤  ПРОФИЛЬ          ║"
MIDDLE_BORDER = "╠═════════════════╣"
BOTTOM_BORDER = "╚═════════════════╝"
EMPTY_LINE = "║                 ║"

def create_profile_text(user_id):
    data = user_data[user_id]
    
    # Собираем профиль построчно строго по формату
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
    
    # Добавляем пользовательские поля (дополнительные строки)
    for field in data['custom_fields']:
        profile_lines.append(MIDDLE_BORDER)
        profile_lines.append(f"║ {field['title']}:")
        # Разбиваем длинный текст на строки по 17 символов
        value_lines = split_text(field['value'], 17)
        for line in value_lines:
            profile_lines.append(f"║ {line}")
        profile_lines.append(EMPTY_LINE)
    
    profile_lines.append(BOTTOM_BORDER)
    return "\n".join(profile_lines)

def split_text(text, max_length):
    """Разбивает текст на строки нужной длины"""
    if len(text) <= max_length:
        return [text]
    
    result = []
    for i in range(0, len(text), max_length):
        result.append(text[i:i+max_length])
    return result

def start(update, context):
    user_id = update.effective_user.id
    
    # Инициализируем данные пользователя со всеми полями
    user_data[user_id] = {
        'name': '',
        'age': '',
        'username': update.effective_user.username or 'Нет username',
        'channel': 'нету',
        'hobby': '',
        'contact': '',
        'best_friend': '',
        'custom_fields': []  # Список пользовательских полей
    }
    
    update.message.reply_text(
        "🌟 **Создание профиля** 🌟\n\n"
        "Давай заполним твою анкету по шагам!\n"
        "Для начала, напиши свое **Имя**:",
        parse_mode='Markdown'
    )
    return NAME

def get_name(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['name'] = update.message.text
    
    update.message.reply_text(
        "✅ Имя сохранено!\n\n"
        "Теперь напиши свой **Возраст**:",
        parse_mode='Markdown'
    )
    return AGE

def get_age(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['age'] = update.message.text
    
    update.message.reply_text(
        "✅ Возраст сохранен!\n\n"
        "Расскажи о своем **Хобби**:",
        parse_mode='Markdown'
    )
    return HOBBY

def get_hobby(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['hobby'] = update.message.text
    
    update.message.reply_text(
        "✅ Хобби сохранено!\n\n"
        "Укажи **Контакт** для связи (email/телефон):",
        parse_mode='Markdown'
    )
    return CONTACT

def get_contact(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['contact'] = update.message.text
    
    update.message.reply_text(
        "✅ Контакт сохранен!\n\n"
        "Кто твой **Best friend**?",
        parse_mode='Markdown'
    )
    return BEST_FRIEND

def get_best_friend(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['best_friend'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("✅ Да, указать канал", callback_data='add_channel')],
        [InlineKeyboardButton("⏭️ Пропустить (будет 'нету')", callback_data='skip_channel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "✅ Best friend сохранен!\n\n"
        "Хочешь указать свой **Telegram канал**?",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return CHANNEL

def channel_callback(update, context):
    query = update.callback_query
    query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == 'skip_channel':
        user_data[user_id]['channel'] = 'нету'
        show_final_profile(update, context)
        return ConversationHandler.END
    else:
        query.edit_message_text("Напиши название или ссылку на твой канал:")
        return CHANNEL

def get_channel(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['channel'] = update.message.text
    show_final_profile(update, context)
    return ConversationHandler.END

def show_final_profile(update, context):
    user_id = update.effective_user.id
    
    # Создаем красивую клавиатуру для управления
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
            update.callback_query.edit_message_text(
                text=f"```\n{profile_text}\n```",
                parse_mode='MarkdownV2',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Ошибка при редактировании: {e}")
    else:
        try:
            update.message.reply_text(
                text=f"```\n{profile_text}\n```",
                parse_mode='MarkdownV2',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке: {e}")

def button_callback(update, context):
    query = update.callback_query
    query.answer()
    
    user_id = update.effective_user.id
    action = query.data
    
    if action == 'refresh':
        show_final_profile(update, context)
    
    elif action == 'restart':
        # Очищаем данные и начинаем заново
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
        query.edit_message_text("Начинаем заполнение заново!\nНапиши свое имя:")
        return NAME
    
    elif action.startswith('edit_'):
        field = action.replace('edit_', '')
        context.user_data['editing_field'] = field
        
        field_names = {
            'name': 'имя',
            'age': 'возраст',
            'hobby': 'хобби',
            'contact': 'контакт',
            'best_friend': 'Best friend',
            'channel': 'канал'
        }
        
        query.edit_message_text(f"Введите новое значение для поля '{field_names[field]}':")
    
    elif action == 'add_field_start':
        context.user_data['editing_field'] = 'new_field_title'
        query.edit_message_text("Введите НАЗВАНИЕ для новой строки (например: 'Город', 'Работа', 'Страна'):")
        return CUSTOM_FIELD_TITLE

def handle_edit_text(update, context):
    user_id = update.effective_user.id
    text = update.message.text
    
    if 'editing_field' in context.user_data:
        field = context.user_data['editing_field']
        
        field_mapping = {
            'name': 'name',
            'age': 'age',
            'hobby': 'hobby',
            'contact': 'contact',
            'best_friend': 'best_friend',
            'channel': 'channel'
        }
        
        if field in field_mapping:
            user_data[user_id][field_mapping[field]] = text
            context.user_data['editing_field'] = None
            show_final_profile(update, context)
    
    return ConversationHandler.END

def get_custom_field_title(update, context):
    user_id = update.effective_user.id
    context.user_data['new_field_title'] = update.message.text
    
    update.message.reply_text(
        f"Теперь введите ЗНАЧЕНИЕ для поля '{update.message.text}':"
    )
    return CUSTOM_FIELD_VALUE

def get_custom_field_value(update, context):
    user_id = update.effective_user.id
    title = context.user_data.get('new_field_title', 'Поле')
    value = update.message.text
    
    user_data[user_id]['custom_fields'].append({
        'title': title,
        'value': value
    })
    
    del context.user_data['new_field_title']
    
    update.message.reply_text(
        f"✅ Строка '{title}' добавлена!"
    )
    
    show_final_profile(update, context)
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text(
        '❌ Заполнение профиля отменено. Начните заново с /start'
    )
    return ConversationHandler.END

def profile(update, context):
    user_id = update.effective_user.id
    
    if user_id not in user_data or not user_data[user_id].get('name'):
        update.message.reply_text(
            "❌ Профиль не найден!\n"
            "Создайте новый с помощью команды /start"
        )
        return
    
    show_final_profile(update, context)

def main():
    # СОЗДАЕМ UPDATER С ПРОКСИ
    request_kwargs = {
        'proxy_url': PROXY
    }
    
    updater = Updater(TOKEN, use_context=True, request_kwargs=request_kwargs)
    dp = updater.dispatcher
    
    # ConversationHandler для последовательного заполнения
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
            CUSTOM_FIELD_TITLE: [MessageHandler(Filters.text & ~Filters.command, get_custom_field_title)],
            CUSTOM_FIELD_VALUE: [MessageHandler(Filters.text & ~Filters.command, get_custom_field_value)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Добавляем обработчики
    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(button_callback, pattern='^(edit_|refresh|restart|add_field_start)'))
    dp.add_handler(CommandHandler('profile', profile))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_edit_text))
    
    print("╔════════════════════════════════╗")
    print("║     🤖 БОТ ЗАПУЩЕН             ║")
    print("╠════════════════════════════════╣")
    print(f"║ Токен: {TOKEN[:10]}... (скрыт)  ║")
    print(f"║ Прокси: {PROXY} ║")
    print("╠════════════════════════════════╣")
    print("║ 📝 /start - создать профиль    ║")
    print("║ 👤 /profile - показать профиль ║")
    print("╚════════════════════════════════╝")
    
    # Запускаем с обработкой ошибок
    while True:
        try:
            updater.start_polling()
            updater.idle()
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("🔄 Перезапуск через 5 секунд...")
            import time
            time.sleep(5)

if __name__ == '__main__':
    main()
