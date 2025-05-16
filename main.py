import os
import json
import logging
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, JobQueue, CallbackContext
)
import asyncio
from dotenv import load_dotenv
from admin_utils import is_admin, add_admin, ensure_first_admin, load_admins

load_dotenv()  # Load .env if exists (local dev)

# Load Firebase credentials from environment and initialize Firebase
firebase_creds = json.loads(os.environ["FIREBASE_CREDENTIALS"])
firebase_db_url = os.getenv("FIREBASE_DB_URL")
if not firebase_db_url:
    raise RuntimeError("FIREBASE_DB_URL environment variable not set")

cred = credentials.Certificate(firebase_creds)
firebase_admin.initialize_app(cred, {
    'databaseURL': firebase_db_url
})

# Load allowed users from env variable (newline or comma separated)
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
    # Firebase returns a dict keyed by task id (string), convert to list
    if isinstance(tasks, dict):
        return list(tasks.values())
    return tasks

async def save_tasks(tasks):
    # Firebase expects dict keyed by ID, convert list to dict
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

    await update.message.reply_text("Hello! DoPing at your service. Use /add, /list, /done commands.")

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
        status = "✅" if t["completed"] else "❌"
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
    if task["completed"]:
        await update.message.reply_text("Task already completed.")
        return

    task["completed"] = True
    await save_tasks(tasks)
    await update.message.reply_text(f"Marked task [{task_id}] as completed.")

async def remind_overdue_tasks(application):
    tasks = await load_tasks()
    now = datetime.utcnow()
    overdue = [t for t in tasks if not t["completed"] and datetime.strptime(t["deadline"], "%Y-%m-%d") < now]
    for task in overdue:
        for admin_id in load_admins():
            try:
                await application.bot.send_message(
                    chat_id=admin_id,
                    text=f"⚠️ Task overdue: [{task['id']}] {task['description']} (due {task['deadline']})"
                )
            except Exception as e:
                logging.error(f"Failed to send reminder to {admin_id}: {e}")

async def remind_callback(context: CallbackContext):
    application = context.application
    await remind_overdue_tasks(application)

async def annoy_users(application):
    admins = load_admins()
    for uid in admins:
        try:
            await application.bot.send_message(
                chat_id=uid,
                text="😠 Why haven’t you completed your tasks yet?!"
            )
        except Exception as e:
            logging.error(f"Annoyance failed: {e}")

async def annoyance_callback(context: CallbackContext):
    application = context.application
    await annoy_users(application)

async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN environment variable not set.")
        return

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_task))
    application.add_handler(CommandHandler("list", list_tasks))
    application.add_handler(CommandHandler("done", done_task))

    print("Bot is running...")

    application.job_queue.run_repeating(remind_callback, interval=3600, first=10)
    application.job_queue.run_repeating(annoyance_callback, interval=7200, first=30)

    await application.run_polling()

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

    application.job_queue.run_repeating(remind_callback, interval=3600, first=10)
    application.job_queue.run_repeating(annoyance_callback, interval=7200, first=30)

    print("Bot is running...")
    application.run_polling()

