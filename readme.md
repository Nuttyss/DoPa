# 🚀 Dopa – Your Minimalist Telegram Productivity Bot

**Dopa** (short for *dopamine*) is a lightweight productivity assistant that lives on Telegram. No bloated apps, no complicated setup — just clean daily focus, nudges when you need them, and small hits of motivation to get things done.

---

## 🎯 What Dopa Helps You Do

✅ Stay focused on your goals  
🔔 Get timely nudges (a.k.a. *dopa-pings*)  
🔐 Optionally restrict usage to your Telegram ID(s)  
🎉 Celebrate task completions with feel-good feedback

---

## 🧠 Features

- 📱 Fully Telegram-based (no extra apps)
- 🔒 Optional access control via `allowed_users.txt`
- 🗂 Simple file-based configuration (no database)
- 🧠 Designed to be AI-ready and extendable
- 🧼 Clean, maintainable Python codebase

---

## ⚙️ Requirements

- Python 3.10+
- [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot) v20+
- [`python-dotenv`](https://pypi.org/project/python-dotenv/)

---

## 🔧 Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/Nuttyss/DoPa_bot.git
   cd DoPa_bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add your Telegram bot token:
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   ```

---

## 👥 User Access Control (Optional)

You can restrict who is allowed to use your bot via a text file named `allowed_users.txt`.

- **Option 1: Allow Everyone** (default)  
  ```txt
  all
  ```

- **Option 2: Restrict to Specific Telegram User IDs**  
  ```txt
  123456789
  987654321
  ```

When a user sends `/start`, their Telegram ID is verified.

---

## ▶️ Running the Bot

```bash
python main.py
```

You should see:
```
🤖 Dopa is running...
```

---

## 🗂 File Structure

```
.
├── .allowed_users        # (Optional) List of allowed Telegram user IDs
├── .env                  # Your Telegram bot token
├── admin_utils.py        # Admin command utilities (optional)
├── dummy_webserver.py    # Lightweight HTTP server for uptime monitoring
├── main.py               # Main entry point
├── notification_utils.py # Handles reminders and nudges
├── sample.py             # Sample or test code
├── requirements.txt      # Python dependencies
└── README.md             # This file!
```

---

## 🛠 Tech Stack

- Python 3.10+
- Telegram Bot API
- `python-telegram-bot`
- `dotenv` for secure environment variable handling

---

## 🔮 Roadmap

### 🔧 Feature Upgrades

- **Dynamic Admin Controls**:  
  `/addadmin <id>`, `/removeadmin <id>`, `/admins` list

- **User Notifications**:  
  Snooze (`/snooze`), mute, and custom reminder intervals

- **Task Enhancements**:  
  Task categories (e.g., Work, Personal), priorities, editing, deadlines

- **Privacy Improvements**:  
  Firebase task isolation per user: `/tasks/<user_id>/`

---

### ☁️ Deployment Plans

- Replace `.env` with secure secrets manager  
- Per-environment Firebase config (dev/prod)  
- GitHub Actions for automatic CI/CD deployments  
- Deployment options: local machine, Render, Firebase Functions, Docker

---

### 🧠 Intelligence Layer (Future)

- **Smart Nudging**: Based on task urgency, completion history  
- **Motivational Messages**: AI-generated encouragement (or guilt 😅)  
- **Adaptive Reminders**: Learn your habits and suggest actions accordingly

---

## 👨‍💻 Author

Built with ❤️ by [Nuttyss](https://github.com/Nuttyss)  
Proudly open-sourced to make productivity less painful.

---

## 🤝 Contributing

Want to contribute ideas or features? Pull requests are welcome.  
Just keep it clean, respectful, and dopamine-friendly.

---

## 📜 License

**MIT** — Free to use, modify, and share.  
Just don’t make it evil.
