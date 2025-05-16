## 🚀 DoPing – Your Personal Telegram Productivity Bot

**DoPing** is a minimalist productivity Telegram bot designed to help you:

* ✅ Stay focused on daily goals
* ✅ Get reminders and nudges (a.k.a. do-pings!)
* ✅ Optionally restrict access to only your Telegram ID(s)
* ✅ Celebrate wins with motivational dopamine hits

---

### 🧠 Features

* 📌 Telegram-based interface (no app needed!)
* 🔐 Optional user access control
* 📂 Simple file-based configuration
* 🧠 Future-proof for AI integration
* 🧠 Built with long-term maintainability in mind

---

### ⚙️ Requirements

* Python 3.10+
* `python-telegram-bot` v20+
* `python-dotenv` (for `.env` handling)

---

### 🔧 Installation

```bash
git clone https://github.com/Nuttyss/DoPinger_bot.git
cd doping-bot
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
BOT_TOKEN=your_telegram_bot_token_here
```

---

### 👥 User Access Control (Optional but Recommended)

You can **control who can use the bot** via an `allowed_users.txt` file.

#### Option 1: Allow everyone (default behavior)

Either leave `allowed_users.txt` **empty** or add `all`:

```txt
all
```

#### Option 2: Restrict to specific Telegram User IDs

```txt
123456789
987654321
```

Your Telegram user ID will be checked automatically when a user sends `/start`.

---

### 🏁 Run the Bot

```bash
python main.py
```

Terminal output:

```
🤖 Bot is running...
```

---

### 📦 Deployment

Currently supports:

* Local desktop/laptop
* Can be adapted for Render, Firebase Cloud Functions, or GitHub + Docker in the future

---

### 📂 File Structure

```
.
├── .allowed_users     # Optional - list of Telegram user IDs
├── .env               # Your bot token lives here
├── main.py            # Main logic
├── requirements.txt   # Required Python dependencies
└── README.md          # You’re reading this!
```

---

### 🛠 Tech Stack

* Python
* Telegram Bot API
* `python-telegram-bot`
* dotenv (for secrets management)

---

### Future Work / Planned Features

The current version of DoPing is stable for basic task management with Firebase-backed persistence. Here are potential future upgrades:
🔧 Feature Improvements

    Dynamic Admin Management:

        Add /addadmin <user_id> and /removeadmin <user_id> commands (admin-only).

        Add /admins command to list current admins.

    User Notifications:

        Let users snooze reminders (/snooze) or customize frequency.

        Add ability to enable/disable annoying reminders per user.

    Task Enhancements:

        Add task priorities and categories (e.g., Work, Personal).

        Support editing or deleting tasks.

        Support time-based deadlines (not just dates).

    Data Privacy / User Isolation:

        Scope tasks per user (instead of shared global task list).

        Add per-user Firebase paths (e.g., /tasks/<user_id>/).

☁️ Deployment Improvements

    Secrets Management:

        Use secrets manager instead of .env for more secure deployment.

        Separate Firebase key per environment (prod/dev).

    CI/CD Integration:

        GitHub Actions to auto-deploy to Render on push.

🧠 Intelligence

    Smart Nudging:

        Use task urgency and history to decide when/how to remind or annoy.

        AI-generated motivation or guilt messages.

### 👨‍💻 Author

Built with love by \Nuttyss.

---