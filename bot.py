import os
import sys
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка более детального логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),  # Логи в stdout для Render
        logging.FileHandler('bot.log')      # Дополнительно в файл
    ]
)
logger = logging.getLogger(__name__)

# Получаем токен
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("❌ Токен бота не найден!")
    logger.error("Установите переменную окружения TELEGRAM_BOT_TOKEN")
    sys.exit(1)

def calculate_compatibility(name1: str, name2: str) -> int:
    """Расчет совместимости на основе нумерологии"""
    # Более сложный расчет (можно модифицировать)
    def name_value(name: str) -> int:
        # Приводим к нижнему регистру и убираем пробелы
        name = name.lower().replace(" ", "")
        # Сумма позиций букв в алфавите (рус+англ)
        total = 0
        for char in name:
            if 'а' <= char <= 'я':
                total += ord(char) - ord('а') + 1
            elif 'a' <= char <= 'z':
                total += ord(char) - ord('a') + 1
        return total
    
    value1 = name_value(name1)
    value2 = name_value(name2)
    
    # Сводим к одной цифре (нумерологическое свертывание)
    def reduce_number(num: int) -> int:
        while num > 9:
            num = sum(int(digit) for digit in str(num))
        return num
    
    score1 = reduce_number(value1)
    score2 = reduce_number(value2)
    
    # Совместимость как среднее значение
    compatibility = (score1 + score2) % 9 + 1
    
    return compatibility

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🔮 *Бот нумерологической совместимости*\n\n"
        "Просто отправьте два имени через пробел, например:\n"
        "• `Анна Иван`\n"
        "• `John Mary`\n\n"
        "Я рассчитаю вашу нумерологическую совместимость!",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    text = update.message.text.strip()
    names = text.split()
    
    if len(names) >= 2:
        name1, name2 = names[0], names[1]
        
        # Расчет совместимости
        score = calculate_compatibility(name1, name2)
        
        # Генерация описания
        descriptions = {
            10: "Идеальная совместимость! 💖",
            9: "Превосходная совместимость! ✨",
            8: "Очень хорошая совместимость! 🌟",
            7: "Хорошая совместимость! 👍",
            6: "Неплохая совместимость! 🤝",
            5: "Средняя совместимость. ⚖️",
            4: "Сложная совместимость. 🤔",
            3: "Низкая совместимость. 💔",
            2: "Очень низкая совместимость. ❌",
            1: "Минимальная совместимость. 🚫"
        }
        
        description = descriptions.get(score, "Нейтральная совместимость.")
        
        await update.message.reply_text(
            f"✨ *Нумерологический анализ* ✨\n\n"
            f"👤 *{name1}* + 👤 *{name2}*\n\n"
            f"🔢 **Уровень совместимости:** {score}/10\n\n"
            f"📊 **Оценка:** {description}\n\n"
            f"💭 *Это развлекательный расчет. Относитесь с юмором!*",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "📝 Пожалуйста, отправьте *два имени* через пробел.\n"
            "Пример: `Анна Иван`",
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")
    if update and update.message:
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

def main():
    """Основная функция запуска бота"""
    logger.info("=" * 50)
    logger.info("🚀 ЗАПУСК NUMEROLOGY BOT")
    logger.info("=" * 50)
    
    try:
        # Создаем приложение
        app = Application.builder().token(TOKEN).build()
        
        # Добавляем обработчики
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Обработчик ошибок
        app.add_error_handler(error_handler)
        
        logger.info("✅ Бот успешно инициализирован")
        logger.info("🔄 Запуск polling...")
        
        # Запускаем бота
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            timeout=30,
            pool_timeout=30,
            close_loop=False
        )
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
