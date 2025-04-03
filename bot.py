import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pytz import timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from database import init_db, save_user, load_user, delete_user

# === Загрузка переменных окружения ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# МСК таймзона
MSK = timezone("Europe/Moscow")

# Исходный список опций (по МСК)
RAW_OPTIONS = [
    ("Вылет: 3 апреля, 09:10", datetime(2025, 4, 3, 9, 10, tzinfo=MSK)),
    ("Прилёт: 3 апреля, 10:50", datetime(2025, 4, 3, 10, 50, tzinfo=MSK)),
    ("Отель: 3 апреля, 17:30", datetime(2025, 4, 3, 17, 30, tzinfo=MSK)),
    ("Илья Койтов на полу: 3 апреля, 22:30", datetime(2025, 4, 3, 22, 30, tzinfo=MSK))
]

# Автогенерация безопасных callback_data
OPTIONS = {f"opt{i+1}": (label, dt) for i, (label, dt) in enumerate(RAW_OPTIONS)}

user_deadlines = {}  # user_id: deadline
user_tasks = {}  # user_id: asyncio.Task

# === Состояния FSM ===
STATE_IDLE = "idle"
STATE_SELECTING = "selecting_time"
STATE_COUNTDOWN = "countdown_started"

# === Команды ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data.clear()

    loaded = load_user(user_id)
    if loaded:
        deadline, state = loaded
        user_deadlines[user_id] = deadline
        context.user_data["state"] = state

        if state == STATE_COUNTDOWN:
            await update.message.reply_text(
                f"Вы уже запустили отсчёт до: {deadline.astimezone(MSK).strftime('%d.%m %H:%M')} (МСК)\n"
                f"Отправлю уведомление каждый час.",
                reply_markup=build_menu()
            )
            app = context.application
            task = asyncio.create_task(start_countdown(app, user_id, deadline))
            user_tasks[user_id] = task
            return

    context.user_data["state"] = STATE_SELECTING
    await update.message.reply_text("Скоро Казань!!\nВыбери время:", reply_markup=build_menu())


def build_menu():
    keyboard = [[InlineKeyboardButton(text=label, callback_data=key)] for key, (label, _) in OPTIONS.items()]
    keyboard.append([
        InlineKeyboardButton("❌ Отменить", callback_data="cancel"),
        InlineKeyboardButton("🔄 Сменить время", callback_data="change")
    ])
    return InlineKeyboardMarkup(keyboard)


def pluralize_hours(n):
    if 11 <= n % 100 <= 14:
        return "часов"
    elif n % 10 == 1:
        return "час"
    elif 2 <= n % 10 <= 4:
        return "часа"
    else:
        return "часов"

def verb_hours(n):
    return "остался" if n % 10 == 1 and not 11 <= n % 100 <= 14 else "осталось"


# === Обработка кнопок ===
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    selected = query.data

    if selected == "cancel":
        await cancel_countdown(user_id, context)
        context.user_data["state"] = STATE_IDLE
        delete_user(user_id)
        await query.edit_message_text("Отсчет отменён. Чтобы начать заново, напиши /start")
        return

    if selected == "change":
        await cancel_countdown(user_id, context)
        context.user_data["state"] = STATE_SELECTING
        await query.edit_message_text("Выбери новое время:", reply_markup=build_menu())
        return

    selected_time_data = OPTIONS.get(selected)
    if not selected_time_data:
        await query.edit_message_text("Ошибка при выборе времени.")
        return

    label, selected_time = selected_time_data
    user_deadlines[user_id] = selected_time
    context.user_data["state"] = STATE_COUNTDOWN
    save_user(user_id, selected_time, STATE_COUNTDOWN)

    await query.edit_message_text(text=f"Отлично! Отсчет до: {label}")

    app = context.application
    task = asyncio.create_task(start_countdown(app, user_id, selected_time))
    user_tasks[user_id] = task


# === Отсчет времени ===
async def start_countdown(app: Application, user_id: int, deadline: datetime):
    while True:
        now = datetime.now(MSK)
        if now >= deadline:
            await app.bot.send_message(chat_id=user_id, text="Ура, Казань!!!!")
            user_deadlines.pop(user_id, None)
            user_tasks.pop(user_id, None)
            delete_user(user_id)
            break
        else:
            hours_left = int((deadline - now).total_seconds() // 3600)
            word = pluralize_hours(hours_left)
            verb = verb_hours(hours_left)
            await app.bot.send_message(chat_id=user_id, text=f"{verb.capitalize()} {hours_left} {word}!!")
            await asyncio.sleep(3600)


# === Отмена отсчета ===
async def cancel_countdown(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    task = user_tasks.pop(user_id, None)
    if task:
        task.cancel()
    user_deadlines.pop(user_id, None)


# === Главная функция ===
def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()