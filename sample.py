from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = '7086088356:AAF6gVF_oDIuwCfZS0HTjayZRFGNSvT3DVw'
ALLOWED_USER_ID = 6328232627  # Replace this with your actual Telegram ID

# Function to check if the user is allowed
def is_authorized(user_id):
    return user_id == ALLOWED_USER_ID

# This function runs when someone sends /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("Access denied.")  # Or just return without replying
        return

    await update.message.reply_text("Hello, Boss! DoPing reporting for duty.")

# Set up the bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add the command handler
    app.add_handler(CommandHandler("start", start))
    
    print("Bot is running...")
    app.run_polling()
