import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
import os
import random

# Включим логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен (твой)
TOKEN = '8755447855:AAEH0FyQbDcVIzQ5ad0E7bkeYLPqoARaF64'

# Прокси (НОВЫЙ РАБОЧИЙ)
PROXY = 'socks5://167.99.233.33:1080'

# Состояния
(NAME, AGE, HOBBY, CONTACT, BEST_FRIEND, CHANNEL, 
 CUSTOM_FIELD_TITLE, CUSTOM_FIELD_VALUE, STYLE_SELECT) = range(9)

# Данные пользователей
user_data = {}

# ================ СТИЛИ ОФОРМЛЕНИЯ (11 штук) ================

STYLES = {
    'classic': {
        'name': '🎭 Классический',
        'top': "╔═════════════════╗",
        'title': "║         👤  ПРОФИЛЬ          ║",
        'middle': "╠═════════════════╣",
        'bottom': "╚═════════════════╝",
        'empty': "║                 ║",
        'side': "║"
    },
    'double': {
        'name': '🔥 Двойной',
        'top': "╔═════════════════╗",
        'title': "║         👤  ПРОФИЛЬ          ║",
        'middle': "╠═════════════════╣",
        'bottom': "╚═════════════════╝",
        'empty': "║                 ║",
        'side': "║"
    },
    'bold': {
        'name': '💪 Жирный',
        'top': "┏━━━━━━━━━━━━━━━━━┓",
        'title': "┃         👤  ПРОФИЛЬ          ┃",
        'middle': "┣━━━━━━━━━━━━━━━━━┫",
        'bottom': "┗━━━━━━━━━━━━━━━━━┛",
        'empty': "┃                 ┃",
        'side': "┃"
    },
    'star': {
        'name': '⭐ Звёздный',
        'top': "✧═════════════════✧",
        'title': "┃         👤  ПРОФИЛЬ          ┃",
        'middle': "┣═════════════════┫",
        'bottom': "✧═════════════════✧",
        'empty': "┃                 ┃",
        'side': "┃"
    },
    'flower': {
        'name': '🌸 Цветочный',
        'top': "╔═════════════════╗",
        'title': "║         👤  ПРОФИЛЬ          ║",
        'middle': "╠═════════════════╣",
        'bottom': "╚═════════════════╝",
        'empty': "║                 ║",
        'side': "║"
    },
    'minimal': {
        'name': '📱 Минимал',
        'top': "┌─────────────────┐",
        'title': "│      👤 ПРОФИЛЬ      │",
        'middle': "├─────────────────┤",
        'bottom': "└─────────────────┘",
        'empty': "│                 │",
        'side': "│"
    },
    'retro': {
        'name': '📺 Ретро',
        'top': "╔═════════════════╗",
        'title': "║         👤  ПРОФИЛЬ          ║",
        'middle': "╠═════════════════╣",
        'bottom': "╚═════════════════╝",
        'empty': "║                 ║",
        'side': "║"
    },
    'neon': {
        'name': '💎 Неон',
        'top': "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰",
        'title': "▰         👤  ПРОФИЛЬ          ▰",
        'middle': "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰",
        'bottom': "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰",
        'empty': "▰                 ▰",
        'side': "▰"
    },
    'elegant': {
        'name': '👑 Элегантный',
        'top': "╭─────────────────╮",
        'title': "│      👤 ПРОФИЛЬ      │",
        'middle': "├─────────────────┤",
        'bottom': "╰─────────────────╯",
        'empty': "│                 │",
        'side': "│"
    },
    'brutal': {
        'name': '🔷 Брутал',
        'top': "╔═════════════════╗",
        'title': "║         👤  ПРОФИЛЬ          ║",
        'middle': "╠═════════════════╣",
        'bottom': "╚═════════════════╝",
        'empty': "║                 ║",
        'side': "║"
    },
    'rainbow': {
        'name': '🌈 Радужный',
        'top': "╔═════════════════╗",
        'title': "║         👤  ПРОФИЛЬ          ║",
        'middle': "╠═════════════════╣",
        'bottom': "╚═════════════════╝",
        'empty': "║                 ║",
        'side': "║"
    }
}

def get_random_style():
    """Возвращает случайный стиль"""
    style_keys = list(STYLES.keys())
    return STYLES[random.choice(style_keys)]

def create_profile_text(user_id, style=None):
    """Создает профиль с выбранным стилем"""
    data = user_data[user_id]
    
    if not style:
        style = STYLES.get(data.get('style', 'classic'), STYLES['classic'])
    
    # Собираем профиль построчно с выбранным стилем
    profile_lines = [
        style['top'],
        style['title'],
        style['middle'],
        f"{style['side']} 📝 Имя: {data['name']}",
        style['middle'],
        f"{style['side']} 📅 Возраст: {data['age']}",
        style['middle'],
        f"{style['side']} 🆔 Username: @{data['username']}",
        style['empty'],
        style['middle'],
        f"{style['side']} 📢 Канал: {data['channel']}",
        style['empty'],
        style['middle'],
        f"{style['side']} 🎨 Хобби:",
        f"{style['side']} {data['hobby']}",
        style['middle'],
        f"{style['side']} 📞 Контакт:",
        f"{style['side']} {data['contact']}",
        style['middle'],
        f"{style['side']} Best friend:",
        f"{style['side']} {data['best_friend']}",
    ]
    
    # Добавляем пользовательские поля
    for field in data['custom_fields']:
        profile_lines.append(style['middle'])
        profile_lines.append(f"{style['side']} {field['title']}:")
        value_lines = split_text(field['value'], 17)
        for line in value_lines:
            profile_lines.append(f"{style['side']} {line}")
        profile_lines.append(style['empty'])
    
    profile_lines.append(style['bottom'])
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
    """Начало работы - выбор стиля"""
    user_id = update.effective_user.id
    
    # Создаем клавиатуру со стилями
    keyboard = []
    row = []
    for i, (style_key, style) in enumerate(STYLES.items()):
        row.append(InlineKeyboardButton(style['name'], callback_data=f'style_{style_key}'))
        if len(row) == 2:  # По 2 кнопки в ряд
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "🎨 **Выбери стиль оформления профиля:**",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return STYLE_SELECT

def style_select(update, context):
    """Обработчик выбора стиля"""
    query = update.callback_query
    query.answer()
    
    user_id = update.effective_user.id
    style_key = query.data.replace('style_', '')
    
    # Инициализируем данные пользователя с выбранным стилем
    user_data[user_id] = {
        'name': '',
        'age': '',
        'username': update.effective_user.username or 'Нет username',
        'channel': 'нету',
        'hobby': '',
        'contact': '',
        'best_friend': '',
        'custom_fields': [],
        'style': style_key
    }
    
    query.edit_message_text(
        "🌟 **Создание профиля** 🌟\n\n"
        f"Выбран стиль: {STYLES[style_key]['name']}\n\n"
        "Для начала, напиши свое **Имя**:",
        parse_mode='Markdown'
    )
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
    
    keyboard = [
        [InlineKeyboardButton("✅ Да, указать канал", callback_data='add_channel')],
        [InlineKeyboardButton("⏭️ Пропустить", callback_data='skip_channel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "✅ Best friend сохранен!\n\nХочешь указать свой канал?",
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
        query.edit_message_text("Напиши название или ссылку на канал:")
        return CHANNEL

def get_channel(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['channel'] = update.message.text
    show_final_profile(update, context)
    return ConversationHandler.END

def show_final_profile(update, context):
    user_id = update.effective_user.id
    style_key = user_data[user_id].get('style', 'classic')
    style = STYLES[style_key]
    
    # Создаем клавиатуру для управления
    keyboard = [
        [InlineKeyboardButton("✏️ Редактировать имя", callback_data='edit_name')],
        [InlineKeyboardButton("✏️ Редактировать возраст", callback_data='edit_age')],
        [InlineKeyboardButton("✏️ Редактировать хобби", callback_data='edit_hobby')],
        [InlineKeyboardButton("✏️ Редактировать контакт", callback_data='edit_contact')],
        [InlineKeyboardButton("✏️ Редактировать Best friend", callback_data='edit_best_friend')],
        [InlineKeyboardButton("✏️ Редактировать канал", callback_data='edit_channel')],
        [InlineKeyboardButton("➕ ДОБАВИТЬ НОВУЮ СТРОКУ", callback_data='add_field_start')],
        [InlineKeyboardButton("🎨 Сменить стиль", callback_data='change_style')],
        [InlineKeyboardButton("🔄 Обновить профиль", callback_data='refresh')],
        [InlineKeyboardButton("❌ Заполнить заново", callback_data='restart')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    profile_text = create_profile_text(user_id, style)
    
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

def change_style(update, context):
    """Меняет стиль профиля"""
    query = update.callback_query
    query.answer()
    
    # Создаем клавиатуру со стилями
    keyboard = []
    row = []
    for i, (style_key, style) in enumerate(STYLES.items()):
        row.append(InlineKeyboardButton(style['name'], callback_data=f'newstyle_{style_key}'))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data='refresh')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        "🎨 **Выбери новый стиль оформления:**",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return STYLE_SELECT

def new_style_select(update, context):
    """Обработчик смены стиля"""
    query = update.callback_query
    query.answer()
    
    user_id = update.effective_user.id
    style_key = query.data.replace('newstyle_', '')
    
    user_data[user_id]['style'] = style_key
    show_final_profile(update, context)
    return ConversationHandler.END

def button_callback(update, context):
    query = update.callback_query
    query.answer()
    
    user_id = update.effective_user.id
    action = query.data
    
    if action == 'refresh':
        show_final_profile(update, context)
    elif action == 'change_style':
        change_style(update, context)
        return STYLE_SELECT
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
                'custom_fields': [],
                'style': user_data[user_id].get('style', 'classic')
            }
        query.edit_message_text("Начинаем заново!\nНапиши свое имя:")
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
    # СОЗДАЕМ UPDATER С РАБОЧИМ ПРОКСИ
    request_kwargs = {
        'proxy_url': PROXY
    }
    
    updater = Updater(TOKEN, use_context=True, request_kwargs=request_kwargs)
    dp = updater.dispatcher
    
    # ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STYLE_SELECT: [
                CallbackQueryHandler(style_select, pattern='^style_'),
                CallbackQueryHandler(new_style_select, pattern='^newstyle_')
            ],
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
    
    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(button_callback, pattern='^(edit_|refresh|restart|add_field_start|change_style)$'))
    dp.add_handler(CommandHandler('profile', profile))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_edit_text))
    
    print("╔════════════════════════════════╗")
    print("║     🤖 БОТ ЗАПУЩЕН             ║")
    print("╠════════════════════════════════╣")
    print(f"║ Токен: {TOKEN[:10]}... (скрыт)  ║")
    print(f"║ Прокси: {PROXY} ║")
    print("╠════════════════════════════════╣")
    print(f"║ 🎨 Доступно стилей: {len(STYLES)}   ║")
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