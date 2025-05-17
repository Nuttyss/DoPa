import os
import json
import logging
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext
)
import asyncio
from dotenv import load_dotenv
from admin_utils import is_admin, add_admin, ensure_first_admin, load_admins

# Hack: Bind a dummy HTTP server to keep Render Web Service happy
try:
    import dummy_webserver
    dummy_webserver.start()
except Exception as e:
    print(f"Dummy webserver failed to start: {e}")

load_dotenv()  # Load .env if exists (local dev)

# Firebase setup
firebase_creds = json.loads(os.environ["FIREBASE_CREDENTIALS"])
firebase_db_url = os.getenv("FIREBASE_DB_URL")
if not firebase_db_url:
    raise RuntimeError("FIREBASE_DB_URL environment variable not set")

cred = credentials.Certificate(firebase_creds)
firebase_admin.initialize_app(cred, {
    'databaseURL': firebase_db_url
})

# Allowed users
allowed_users_env = os.getenv("ALLOWED_USERS", "").strip()
if allowed_users_env:
    ALLOWED_USERS = set(int(uid.strip()) for uid in allowed_users_env.replace(",", "\n").splitlines() if uid.strip())
else:
    ALLOWED_USERS = None  # No restriction

def is_user_allowed(user_id: int) -> bool:
    if ALLOWED_USERS is None:
        return True
    return user_id in ALLOWED_USERS

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Firebase keys
TASKS_DB_REF = "tasks"

async def load_tasks():
    tasks = db.reference(TASKS_DB_REF).get()
    if not tasks:
        return []
    if isinstance(tasks, dict):
        return [t for t in tasks.values() if isinstance(t, dict)]
    return [t for t in tasks if isinstance(t, dict)]

async def save_tasks(tasks):
    tasks_dict = {str(t["id"]): t for t in tasks}
    db.reference(TASKS_DB_REF).set(tasks_dict)

def get_task_by_id(tasks, task_id):
    for t in tasks:
        if t["id"] == task_id:
            return t
    return None

def generate_task_id(tasks):
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_first_admin(user_id)

    if not is_user_allowed(user_id):
        await update.message.reply_text("Access denied.")
        return

    await update.message.reply_text("Hello! DoPing at your service. Use /add, /list, /done.")

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_allowed(user_id):
        await update.message.reply_text("Access denied.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage: /add <deadline YYYY-MM-DD> <task description>")
        return

    deadline_str = context.args[0]
    description = " ".join(context.args[1:])

    try:
        datetime.strptime(deadline_str, "%Y-%m-%d")
    except ValueError:
        await update.message.reply_text("Invalid date format. Use YYYY-MM-DD.")
        return

    tasks = await load_tasks()
    task_id = generate_task_id(tasks)
    task = {
        "id": task_id,
        "description": description,
        "deadline": deadline_str,
        "completed": False,
        "created_at": datetime.utcnow().isoformat()
    }
    tasks.append(task)
    await save_tasks(tasks)

    await update.message.reply_text(f"Task added: [{task_id}] {description} (due {deadline_str})")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_allowed(user_id):
        await update.message.reply_text("Access denied.")
        return

    tasks = await load_tasks()
    if not tasks:
        await update.message.reply_text("No tasks found.")
        return

    lines = []
    for t in tasks:
        if t is None:
            continue
        status = "✅" if t.get("completed") else "❌"
        lines.append(f"[{t['id']}] {status} {t['description']} (due {t['deadline']})")
    await update.message.reply_text("\n".join(lines))

async def done_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_allowed(user_id):
        await update.message.reply_text("Access denied.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /done <task_id>")
        return

    try:
        task_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Task ID must be a number.")
        return

    tasks = await load_tasks()
    task = get_task_by_id(tasks, task_id)
    if not task:
        await update.message.reply_text(f"No task found with ID {task_id}.")
        return
    if task.get("completed"):
        await update.message.reply_text("Task already completed.")
        return

    task["completed"] = True
    await save_tasks(tasks)
    await update.message.reply_text(f"Marked task [{task_id}] as completed.")

async def remind_users(application):
    tasks = await load_tasks()
    now = datetime.utcnow()

    encouragements = []
    warnings = []

    for t in tasks:
        if t.get("completed"):
            continue

        deadline = datetime.strptime(t["deadline"], "%Y-%m-%d")
        if deadline.date() < now.date():
            warnings.append(t)
        elif deadline.date() == now.date():
            encouragements.append(t)

    admins = load_admins()
    for uid in admins:
        if encouragements:
            await application.bot.send_message(
                chat_id=uid,
                text="💪 Keep going! You still have tasks to finish today!"
            )
        for task in warnings:
            await application.bot.send_message(
                chat_id=uid,
                text=f"😠 Why haven’t you completed: [{task['id']}] {task['description']} (due {task['deadline']})"
            )

async def reminder_callback(context: CallbackContext):
    await remind_users(context.application)

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    token = os.getenv("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN environment variable not set.")
        exit(1)

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_task))
    application.add_handler(CommandHandler("list", list_tasks))
    application.add_handler(CommandHandler("done", done_task))

    # Reminder job
    application.job_queue.run_repeating(reminder_callback, interval=3600, first=10)

    print("Bot is running...")
    application.run_polling()
