import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
import os
import random
from datetime import datetime

# Включим логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен
TOKEN = os.getenv('BOT_TOKEN')

# Состояния
(NAME, AGE, HOBBY, CONTACT, BEST_FRIEND, CHANNEL, CUSTOM, DECORATION) = range(8)

# Данные пользователей
user_data = {}

# Коллекция украшений
DECORATIONS = {
    # Классические рамки
    'classic': {
        'top': "╔════════════════════════╗",
        'title_top': "║                        ║",
        'title': "║        👤 ПРОФИЛЬ        ║",
        'title_bottom': "║                        ║",
        'mid': "╠════════════════════════╣",
        'empty': "║                        ║",
        'bottom': "╚════════════════════════╝"
    },
    
    # Двойная рамка
    'double': {
        'top': "╔════════════════════════╗",
        'title_top': "║                        ║",
        'title': "║    ╔══════════════╗     ║",
        'title_mid': "║    ║   ПРОФИЛЬ    ║     ║",
        'title_bottom': "║    ╚══════════════╝     ║",
        'mid': "╠════════════════════════╣",
        'empty': "║                        ║",
        'bottom': "╚════════════════════════╝"
    },
    
    # Звездная тема
    'star': {
        'top': "⭐══════════════════════⭐",
        'title_top': "⍟                        ⍟",
        'title': "⍟       ПРОФИЛЬ         ⍟",
        'title_bottom': "⍟                        ⍟",
        'mid': "✧══════════════════════✧",
        'empty': "⍟                        ⍟",
        'bottom': "⭐══════════════════════⭐"
    },
    
    # Цветочная тема
    'flower': {
        'top': "✿══════════════════════✿",
        'title_top': "❀                        ❀",
        'title': "❀       ПРОФИЛЬ         ❀",
        'title_bottom': "❀                        ❀",
        'mid': "✽══════════════════════✽",
        'empty': "❀                        ❀",
        'bottom': "✿══════════════════════✿"
    },
    
    # Неоновая тема
    'neon': {
        'top': "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰",
        'title_top': "█                        █",
        'title': "█       ПРОФИЛЬ         █",
        'title_bottom': "█                        █",
        'mid': "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰",
        'empty': "█                        █",
        'bottom': "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰"
    },
    
    # Морская тема
    'ocean': {
        'top': "🌊══════════════════════🌊",
        'title_top': "~                        ~",
        'title': "~       ПРОФИЛЬ         ~",
        'title_bottom': "~                        ~",
        'mid': "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️",
        'empty': "~                        ~",
        'bottom': "🌊══════════════════════🌊"
    },
    
    # Кибер-тема
    'cyber': {
        'top': "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯",
        'title_top': "╭────────────────────────╮",
        'title': "│        ПРОФИЛЬ         │",
        'title_bottom': "╰────────────────────────╯",
        'mid': "══════════════════════════",
        'empty': "│                        │",
        'bottom': "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"
    },
    
    # Романтическая тема
    'romantic': {
        'top': "❤️══════════════════════❤️",
        'title_top': "♡                        ♡",
        'title': "♡       ПРОФИЛЬ         ♡",
        'title_bottom': "♡                        ♡",
        'mid': "💗══════════════════════💗",
        'empty': "♡                        ♡",
        'bottom': "❤️══════════════════════❤️"
    },
    
    # Фэнтези тема
    'fantasy': {
        'top': "✨══════════════════════✨",
        'title_top': "★                        ★",
        'title': "★       ПРОФИЛЬ         ★",
        'title_bottom': "★                        ★",
        'mid': "⚡══════════════════════⚡",
        'empty': "★                        ★",
        'bottom': "✨══════════════════════✨"
    },
    
    # Минимализм
    'minimal': {
        'top': "┌────────────────────────┐",
        'title_top': "│                        │",
        'title': "│        ПРОФИЛЬ         │",
        'title_bottom': "│                        │",
        'mid': "├────────────────────────┤",
        'empty': "│                        │",
        'bottom': "└────────────────────────┘"
    },
    
    # Ретро тема
    'retro': {
        'top': "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄",
        'title_top': "█                        █",
        'title': "█       ПРОФИЛЬ         █",
        'title_bottom': "█                        █",
        'mid': "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀",
        'empty': "█                        █",
        'bottom': "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"
    }
}

# Разделители для разных стилей
SEPARATORS = {
    'classic': "════════════════════════",
    'double': "════════════════════════",
    'star': "✧══════════════════════✧",
    'flower': "✽══════════════════════✽",
    'neon': "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰",
    'ocean': "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️",
    'cyber': "══════════════════════════",
    'romantic': "💗══════════════════════💗",
    'fantasy': "⚡══════════════════════⚡",
    'minimal': "────────────────────────",
    'retro': "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀"
}

# Иконки для полей
FIELD_ICONS = {
    'name': ['📝', '👤', '✨', '🎭', '💫', '🌟', '🎪', '🎨'],
    'age': ['📅', '🎂', '🗓️', '⏳', '⌛', '📆', '🎈', '🕯️'],
    'username': ['🆔', '🔖', '🏷️', '📌', '📍', '🎫', '💳', '🔑'],
    'channel': ['📢', '📺', '📡', '🎥', '📻', '💬', '🗣️', '🔊'],
    'hobby': ['🎨', '🎮', '🎵', '⚽', '📚', '🎯', '🎪', '🎭'],
    'contact': ['📞', '💬', '📱', '✉️', '📧', '💌', '📨', '📲'],
    'best_friend': ['🤝', '💕', '👥', '💑', '👬', '👭', '💗', '💖'],
    'custom': ['💭', '✨', '📝', '🎵', '💫', '⭐', '💢', '💥']
}

# Эмодзи для статусов
STATUS_EMOJIS = ['🌞', '🌙', '⭐', '☀️', '🌈', '⚡', '🔥', '💧', '🌪️', '❄️']

def get_random_icon(field):
    """Получить случайную иконку для поля"""
    return random.choice(FIELD_ICONS.get(field, ['📌']))

def format_text(text, width=22):
    """Форматировать текст для вставки в рамку"""
    if len(text) > width:
        return text[:width-3] + "..."
    return text

def make_profile(user_id, decoration_style='classic'):
    data = user_data.get(user_id, {})
    deco = DECORATIONS.get(decoration_style, DECORATIONS['classic'])
    
    # Добавляем случайный статус
    status = random.choice(STATUS_EMOJIS)
    
    lines = [
        deco['top'],
        deco['title_top'],
        deco['title'],
        deco['title_bottom'],
        deco['mid'],
        f"║ {get_random_icon('name')} Имя: {format_text(data.get('name', ''))}",
        deco['mid'],
        f"║ {get_random_icon('age')} Возраст: {format_text(data.get('age', ''))}",
        deco['mid'],
        f"║ {get_random_icon('username')} Username: @{format_text(data.get('username', 'нет'))}",
        deco['empty'],
        deco['mid'],
        f"║ {get_random_icon('channel')} Канал: {format_text(data.get('channel', 'нету'))}",
        deco['empty'],
        deco['mid'],
        f"║ {get_random_icon('hobby')} Хобби:",
        f"║ {format_text(data.get('hobby', ''))}",
        deco['mid'],
        f"║ {get_random_icon('contact')} Контакт:",
        f"║ {format_text(data.get('contact', ''))}",
        deco['mid'],
        f"║ {get_random_icon('best_friend')} Best friend:",
        f"║ {format_text(data.get('best_friend', ''))}",
        deco['mid'],
        f"║ {get_random_icon('custom')} Дополнительно:",
        f"║ {format_text(data.get('custom', ''))}",
        deco['empty'],
        f"║ Статус: {status}",
        deco['bottom']
    ]
    
    # Добавляем время создания/обновления
    if 'created_at' not in data:
        data['created_at'] = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    lines.insert(-2, f"║ 🕒 {data['created_at']}")
    
    return "\n".join(lines)

def start(update, context):
    user_id = update.effective_user.id
    user_data[user_id] = {
        'name': '', 'age': '', 'hobby': '', 'contact': '', 
        'best_friend': '', 'channel': 'нету', 'custom': '',
        'username': update.effective_user.username or 'нет',
        'created_at': datetime.now().strftime("%d.%m.%Y %H:%M"),
        'decoration_style': 'classic'
    }
    
    # Красивое приветствие
    welcome_text = """
🌟 **Добро пожаловать в конструктор профиля!** 🌟

Я помогу тебе создать красивую мини-биографию с уникальным оформлением.

✨ **Что тебя ждет:**
• Множество стилей оформления
• Красивые рамки и разделители
• Уникальные иконки для каждого поля
• Случайные статусы и эмодзи
• Возможность добавить свою информацию

📝 **Давай начнем! Напиши свое имя:**
    """
    
    update.message.reply_text(welcome_text, parse_mode='Markdown')
    return NAME

def get_name(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['name'] = update.message.text
    update.message.reply_text(
        f"✅ {get_random_icon('name')} Имя сохранено!\n\n"
        f"📅 Теперь напиши свой **Возраст**:",
        parse_mode='Markdown'
    )
    return AGE

def get_age(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['age'] = update.message.text
    update.message.reply_text(
        f"✅ {get_random_icon('age')} Возраст сохранен!\n\n"
        f"🎨 Расскажи о своем **Хобби**:",
        parse_mode='Markdown'
    )
    return HOBBY

def get_hobby(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['hobby'] = update.message.text
    update.message.reply_text(
        f"✅ {get_random_icon('hobby')} Хобби сохранено!\n\n"
        f"📞 Укажи **Контакт** для связи:",
        parse_mode='Markdown'
    )
    return CONTACT

def get_contact(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['contact'] = update.message.text
    update.message.reply_text(
        f"✅ {get_random_icon('contact')} Контакт сохранен!\n\n"
        f"🤝 Кто твой **Best friend**?",
        parse_mode='Markdown'
    )
    return BEST_FRIEND

def get_best_friend(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['best_friend'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("📢 Указать канал", callback_data='add_channel')],
        [InlineKeyboardButton("⏭️ Пропустить", callback_data='skip_channel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "📺 Хочешь указать свой канал или Telegram канал?",
        reply_markup=reply_markup
    )
    return CHANNEL

def channel_callback(update, context):
    query = update.callback_query
    query.answer()
    
    if query.data == 'skip_channel':
        show_style_selection(update, context)
        return DECORATION
    else:
        query.edit_message_text(
            f"{get_random_icon('channel')} Напиши название канала:"
        )
        return CHANNEL

def get_channel(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['channel'] = update.message.text
    show_style_selection(update, context)
    return DECORATION

def show_style_selection(update, context):
    """Показать выбор стиля оформления"""
    keyboard = []
    
    # Создаем кнопки для всех стилей (по 2 в ряд)
    styles = list(DECORATIONS.keys())
    for i in range(0, len(styles), 2):
        row = []
        row.append(InlineKeyboardButton(
            f"{get_style_emoji(styles[i])} {styles[i].title()}",
            callback_data=f'style_{styles[i]}'
        ))
        if i + 1 < len(styles):
            row.append(InlineKeyboardButton(
                f"{get_style_emoji(styles[i+1])} {styles[i+1].title()}",
                callback_data=f'style_{styles[i+1]}'
            ))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🎲 Случайный стиль", callback_data='style_random')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🎨 **Выбери стиль оформления профиля!**

Каждый стиль уникален:
• Классический - строгий и элегантный
• Двойная рамка - объемный дизайн
• Звездный - космическая тематика
• Цветочный - нежный и романтичный
• Неоновый - яркий и современный
• Морской - свежий и легкий
• Кибер - футуристический стиль
• Романтичный - для сердечек
• Фэнтези - магическая атмосфера
• Минимализм - просто и со вкусом
• Ретро - винтажный стиль

Выбери свой стиль:
    """
    
    if hasattr(update, 'callback_query') and update.callback_query:
        update.callback_query.edit_message_text(
            text=text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text(
            text=text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

def get_style_emoji(style):
    """Получить эмодзи для стиля"""
    emojis = {
        'classic': '📋',
        'double': '📦',
        'star': '⭐',
        'flower': '🌸',
        'neon': '💡',
        'ocean': '🌊',
        'cyber': '🤖',
        'romantic': '❤️',
        'fantasy': '🧙',
        'minimal': '◻️',
        'retro': '📻'
    }
    return emojis.get(style, '🎨')

def style_callback(update, context):
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    
    if query.data == 'style_random':
        style = random.choice(list(DECORATIONS.keys()))
    else:
        style = query.data.replace('style_', '')
    
    user_data[user_id]['decoration_style'] = style
    
    # Показываем предпросмотр
    show_profile_with_style(update, context, style)

def show_profile_with_style(update, context, style):
    """Показать профиль с выбранным стилем"""
    user_id = update.effective_user.id
    
    keyboard = [
        [
            InlineKeyboardButton("🎨 Сменить стиль", callback_data='change_style'),
            InlineKeyboardButton("➕ Добавить строку", callback_data='add_custom')
        ],
        [
            InlineKeyboardButton("🔄 Обновить", callback_data='refresh'),
            InlineKeyboardButton("📋 Поделиться", callback_data='share')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = make_profile(user_id, style)
    
    # Экранируем спецсимволы для MarkdownV2
    text = text.replace('-', '\\-').replace('.', '\\.').replace('!', '\\!')
    
    query = update.callback_query
    query.edit_message_text(
        text=f"```\n{text}\n```",
        parse_mode='MarkdownV2',
        reply_markup=reply_markup
    )

def button_handler(update, context):
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    
    if query.data == 'refresh':
        style = user_data.get(user_id, {}).get('decoration_style', 'classic')
        show_profile_with_style(update, context, style)
    elif query.data == 'change_style':
        show_style_selection(update, context)
        return DECORATION
    elif query.data == 'add_custom':
        query.edit_message_text(
            f"{get_random_icon('custom')} Введите текст для дополнительной информации:"
        )
        return CUSTOM
    elif query.data == 'share':
        style = user_data.get(user_id, {}).get('decoration_style', 'classic')
        text = make_profile(user_id, style)
        query.edit_message_text(
            f"📋 **Твой красивый профиль готов!**\n\n"
            f"```\n{text}\n```\n\n"
            f"Скопируй и поделись с друзьями! 🎉",
            parse_mode='Markdown'
        )

def get_custom(update, context):
    user_id = update.effective_user.id
    user_data[user_id]['custom'] = update.message.text
    
    # Показываем профиль с текущим стилем
    style = user_data.get(user_id, {}).get('decoration_style', 'classic')
    
    keyboard = [
        [
            InlineKeyboardButton("🎨 Сменить стиль", callback_data='change_style'),
            InlineKeyboardButton("🔄 Обновить", callback_data='refresh')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = make_profile(user_id, style)
    text = text.replace('-', '\\-').replace('.', '\\.').replace('!', '\\!')
    
    update.message.reply_text(
        text=f"```\n{text}\n```",
        parse_mode='MarkdownV2',
        reply_markup=reply_markup
    )
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text(
        f"❌ Создание профиля отменено.\n"
        f"Начни заново с команды /start"
    )
    return ConversationHandler.END

def main():
    # СОЗДАЕМ UPDATER
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
            DECORATION: [
                CallbackQueryHandler(style_callback, pattern='^style_')
            ],
            CUSTOM: [MessageHandler(Filters.text & ~Filters.command, get_custom)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(button_handler, pattern='^(refresh|change_style|add_custom|share)$'))
    
    # Добавляем команду для быстрого просмотра профиля
    def profile_command(update, context):
        user_id = update.effective_user.id
        if user_id in user_data:
            style = user_data[user_id].get('decoration_style', 'classic')
            text = make_profile(user_id, style)
            text = text.replace('-', '\\-').replace('.', '\\.').replace('!', '\\!')
            
            keyboard = [[InlineKeyboardButton("🎨 Сменить стиль", callback_data='change_style')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            update.message.reply_text(
                text=f"```\n{text}\n```",
                parse_mode='MarkdownV2',
                reply_markup=reply_markup
            )
        else:
            update.message.reply_text(
                "❌ У тебя еще нет профиля! Создай его с помощью /start"
            )
    
    dp.add_handler(CommandHandler('profile', profile_command))
    
    print("✅ БОТ ЗАПУЩЕН С НОВЫМ ДИЗАЙНОМ!")
    print(f"🤖 Токен: {TOKEN[:10]}... (скрыт)")
    print("🎨 Доступно стилей:", len(DECORATIONS))
    
    # Запускаем
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()