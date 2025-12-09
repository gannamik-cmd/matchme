import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ContextTypes, 
    filters
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Нумерологические значения букв (кириллица)
NUMEROLOGY_VALUES = {
    'А': 1, 'Б': 2, 'В': 3, 'Г': 4, 'Д': 5, 'Е': 6, 'Ё': 7, 'Ж': 8, 'З': 9,
    'И': 1, 'Й': 2, 'К': 3, 'Л': 4, 'М': 5, 'Н': 6, 'О': 7, 'П': 8, 'Р': 9,
    'С': 1, 'Т': 2, 'У': 3, 'Ф': 4, 'Х': 5, 'Ц': 6, 'Ч': 7, 'Ш': 8, 'Щ': 9,
    'Ъ': 1, 'Ы': 2, 'Ь': 3, 'Э': 4, 'Ю': 5, 'Я': 6,
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
}

# Ключевые слова для совместимости
COMPATIBILITY_KEYWORDS = {
    1: "Лидерство и инициатива",
    2: "Гармония и партнерство",
    3: "Творчество и общение",
    4: "Стабильность и практичность",
    5: "Свобода и перемены",
    6: "Забота и ответственность",
    7: "Мудрость и анализ",
    8: "Успех и изобилие",
    9: "Гуманизм и сострадание"
}

# Функции для нумерологических расчетов
def reduce_to_single_digit(number):
    """Сводит число к одной цифре (1-9)"""
    while number > 9:
        number = sum(int(digit) for digit in str(number))
    return number

def calculate_name_number(name):
    """Рассчитывает нумерологическое число имени"""
    total = 0
    for char in name.upper():
        if char in NUMEROLOGY_VALUES:
            total += NUMEROLOGY_VALUES[char]
    return reduce_to_single_digit(total)

def calculate_birthdate_number(date_str):
    """Рассчитывает нумерологическое число даты рождения"""
    try:
        # Пробуем разные форматы даты
        formats = ['%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']
        date_obj = None
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        
        if not date_obj:
            return None
            
        day = date_obj.day
        month = date_obj.month
        year = date_obj.year
        
        total = day + month + year
        return reduce_to_single_digit(total)
    except Exception as e:
        logger.error(f"Ошибка расчета даты: {e}")
        return None

def calculate_compatibility(number1, number2):
    """Рассчитывает совместимость двух чисел"""
    compatibility_number = reduce_to_single_digit(number1 + number2)
    
    # Описания совместимости
    compatibility_descriptions = {
        1: "Отличная совместимость! Вы созданы для совместных достижений и лидерства.",
        2: "Гармоничный союз. Вы дополняете друг друга и создаете баланс.",
        3: "Творческая совместимость. Вместе вы можете создавать нечто удивительное.",
        4: "Стабильные отношения. Вы строите прочный фундамент для будущего.",
        5: "Динамичный союз. Вас ждут приключения и перемены вместе.",
        6: "Заботливые отношения. Вы создаете уют и гармонию в паре.",
        7: "Мудрый союз. Вы учитесь друг у друга и растете вместе.",
        8: "Деловая совместимость. Вы можете достичь больших успехов вместе.",
        9: "Духовная связь. Ваши отношения имеют глубокий смысл."
    }
    
    percentage = (compatibility_number * 11) % 100
    if percentage < 30:
        percentage += 30
    
    return {
        'number': compatibility_number,
        'percentage': percentage,
        'description': compatibility_descriptions.get(compatibility_number, "Особенная совместимость!"),
        'keywords': COMPATIBILITY_KEYWORDS.get(compatibility_number, "Уникальная энергия")
    }

# Команды бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    keyboard = [
        [InlineKeyboardButton("📛 Совместимость имён", callback_data='name_comp')],
        [InlineKeyboardButton("📅 Совместимость по дате рождения", callback_data='date_comp')],
        [InlineKeyboardButton("❓ Помощь", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        "Я - бот нумерологической совместимости! 🔮\n\n"
        "Я могу помочь вам рассчитать совместимость:\n"
        "• По именам\n"
        "• По датам рождения\n\n"
        "Выберите опцию ниже:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📚 *Помощь по использованию бота:*

*Доступные команды:*
/start - Запустить бота
/help - Получить справку
/name - Проверить совместимость имен
/date - Проверить совместимость по датам рождения

*Как пользоваться:*
1. Выберите тип совместимости
2. Введите данные по запросу бота
3. Получите подробный анализ совместимости

*Примеры ввода даты:*
• 15.08.1990
• 15/08/1990
• 15-08-1990
• 1990-08-15

*Примечание:* Имена можно вводить на русском или английском языке.
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def name_compatibility(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /name"""
    await update.message.reply_text(
        "📛 *Совместимость имён*\n\n"
        "Введите два имени через пробел или запятую:\n"
        "Пример: *Анна Иван* или *Anna, John*",
        parse_mode='Markdown'
    )
    context.user_data['awaiting'] = 'names'

async def date_compatibility(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /date"""
    await update.message.reply_text(
        "📅 *Совместимость по дате рождения*\n\n"
        "Введите две даты рождения через пробел или запятую:\n"
        "Пример: *15.08.1990 20.05.1985*",
        parse_mode='Markdown'
    )
    context.user_data['awaiting'] = 'dates'

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий кнопок"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'name_comp':
        await query.edit_message_text(
            text="📛 *Совместимость имён*\n\n"
                 "Введите два имени через пробел или запятую:\n"
                 "Пример: *Анна Иван* или *Anna, John*",
            parse_mode='Markdown'
        )
        context.user_data['awaiting'] = 'names'
    
    elif query.data == 'date_comp':
        await query.edit_message_text(
            text="📅 *Совместимость по дате рождения*\n\n"
                 "Введите две даты рождения через пробел или запятую:\n"
                 "Пример: *15.08.1990 20.05.1985*",
            parse_mode='Markdown'
        )
        context.user_data['awaiting'] = 'dates'
    
    elif query.data == 'help':
        help_text = """
📚 *Помощь по использованию бота:*

*Доступные команды:*
/start - Запустить бота
/help - Получить справку
/name - Проверить совместимость имен
/date - Проверить совместимость по датам рождения

*Как пользоваться:*
1. Выберите тип совместимости
2. Введите данные по запросу бота
3. Получите подробный анализ совместимости

*Примеры ввода даты:*
• 15.08.1990
• 15/08/1990
• 15-08-1990
• 1990-08-15

*Примечание:* Имена можно вводить на русском или английском языке.
        """
        await query.edit_message_text(text=help_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_message = update.message.text.strip()
    user_data = context.user_data
    
    if 'awaiting' not in user_data:
        await update.message.reply_text(
            "Пожалуйста, выберите опцию через меню или используйте команды:\n"
            "/name - совместимость имён\n"
            "/date - совместимость по дате рождения\n"
            "/help - помощь"
        )
        return
    
    if user_data['awaiting'] == 'names':
        # Обработка имён
        separators = [',', ';', ' и ', '&']
        names = user_message
        
        for sep in separators:
            if sep in names:
                names = names.split(sep)
                break
        else:
            names = names.split()
        
        if len(names) < 2:
            await update.message.reply_text(
                "Пожалуйста, введите два имени.\n"
                "Пример: *Анна Иван* или *Anna, John*",
                parse_mode='Markdown'
            )
            return
        
        name1 = names[0].strip()
        name2 = names[1].strip()
        
        # Рассчитываем числа имён
        number1 = calculate_name_number(name1)
        number2 = calculate_name_number(name2)
        
        # Рассчитываем совместимость
        compatibility = calculate_compatibility(number1, number2)
        
        # Формируем ответ
        response = (
            f"🔮 *Результаты совместимости имён:*\n\n"
            f"*Имя 1:* {name1}\n"
            f"*Число имени:* {number1} - {COMPATIBILITY_KEYWORDS.get(number1, '')}\n\n"
            f"*Имя 2:* {name2}\n"
            f"*Число имени:* {number2} - {COMPATIBILITY_KEYWORDS.get(number2, '')}\n\n"
            f"📊 *Совместимость:* {compatibility['percentage']}%\n"
            f"*Число совместимости:* {compatibility['number']}\n"
            f"*Ключевые слова:* {compatibility['keywords']}\n\n"
            f"💫 *Описание:*\n{compatibility['description']}\n\n"
            f"_Числа помогают понять потенциал отношений, но помните, что реальные отношения строятся на взаимопонимании и уважении._"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        user_data.pop('awaiting', None)
    
    elif user_data['awaiting'] == 'dates':
        # Обработка дат рождения
        separators = [',', ';', ' и ', '&']
        dates_input = user_message
        
        for sep in separators:
            if sep in dates_input:
                dates = dates_input.split(sep)
                break
        else:
            dates = dates_input.split()
        
        if len(dates) < 2:
            await update.message.reply_text(
                "Пожалуйста, введите две даты рождения.\n"
                "Пример: *15.08.1990 20.05.1985*",
                parse_mode='Markdown'
            )
            return
        
        date1 = dates[0].strip()
        date2 = dates[1].strip()
        
        # Рассчитываем числа дат рождения
        number1 = calculate_birthdate_number(date1)
        number2 = calculate_birthdate_number(date2)
        
        if number1 is None or number2 is None:
            await update.message.reply_text(
                "Пожалуйста, введите даты в правильном формате.\n"
                "Примеры: *15.08.1990*, *15/08/1990*, *1990-08-15*",
                parse_mode='Markdown'
            )
            return
        
        # Рассчитываем совместимость
        compatibility = calculate_compatibility(number1, number2)
        
        # Формируем ответ
        response = (
            f"🔮 *Результаты совместимости по дате рождения:*\n\n"
            f"*Дата 1:* {date1}\n"
            f"*Число судьбы:* {number1} - {COMPATIBILITY_KEYWORDS.get(number1, '')}\n\n"
            f"*Дата 2:* {date2}\n"
            f"*Число судьбы:* {number2} - {COMPATIBILITY_KEYWORDS.get(number2, '')}\n\n"
            f"📊 *Совместимость:* {compatibility['percentage']}%\n"
            f"*Число совместимости:* {compatibility['number']}\n"
            f"*Ключевые слова:* {compatibility['keywords']}\n\n"
            f"💫 *Описание:*\n{compatibility['description']}\n\n"
            f"_Числа судьбы показывают потенциал совместимости, но настоящие отношения требуют усилий и взаимопонимания._"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        user_data.pop('awaiting', None)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")
    
    try:
        await update.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте снова или используйте /help для справки."
        )
    except:
        pass

def main():
    """Основная функция запуска бота"""
    # Получаем токен из переменных окружения
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не установлен!")
        return
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("name", name_compatibility))
    application.add_handler(CommandHandler("date", date_compatibility))
    
    # Регистрируем обработчики кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    port = int(os.environ.get('PORT', 8443))
    
    if os.getenv('RENDER'):
        # На Render используем вебхук
        webhook_url = os.getenv('RENDER_EXTERNAL_URL')
        if webhook_url:
            application.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=TOKEN,
                webhook_url=f"{webhook_url}/{TOKEN}"
            )
        else:
            logger.error("RENDER_EXTERNAL_URL не установлен!")
    else:
        # Локально используем polling
        application.run_polling()

if __name__ == '__main__':
    main()
