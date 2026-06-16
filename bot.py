import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = "8940425073:AAEtydG4kvCGUBN90pW7Uqmmwuf1NQd01qw"

logging.basicConfig(level=logging.INFO)

def load_serials():
    try:
        with open("serials.json", "r") as f:
            return json.load(f)
    except:
        return {}

SERIALS = load_serials()
EPISODES_PER_PAGE = 5

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    available = ", ".join(SERIALS.keys())
    await update.message.reply_text(f"👋 Welcome to VjTvDaily Bot!\n\nAvailable serials:\n{available}\n\nJust type the serial name!")

async def search_serial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_term = update.message.text.lower().strip()
    matching_serial = None
    for serial_name in SERIALS.keys():
        if search_term in serial_name or serial_name in search_term:
            matching_serial = serial_name
            break
    if not matching_serial:
        available = ", ".join(SERIALS.keys())
        await update.message.reply_text(f"❌ Not found!\n\nAvailable: {available}")
        return
    await show_episodes(update, matching_serial, page=0)

async def show_episodes(update, serial_name, page=0):
    episodes = SERIALS.get(serial_name, [])
    start_idx = page * EPISODES_PER_PAGE
    end_idx = start_idx + EPISODES_PER_PAGE
    page_episodes = episodes[start_idx:end_idx]
    if not page_episodes:
        return
    message = f"📺 {serial_name.upper()}\n"
    message += f"Episodes {start_idx + 1}-{min(end_idx, len(episodes))} of {len(episodes)}\n\n"
    for idx, ep in enumerate(page_episodes, start=start_idx + 1):
        message += f"Episode {idx} - {ep['date']}\n"
    buttons = []
    row = []
    if page > 0:
        row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"page_{serial_name}_{page-1}"))
    if end_idx < len(episodes):
        row.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{serial_name}_{page+1}"))
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔍 New Search", callback_data="new_search")])
    markup = InlineKeyboardMarkup(buttons)
    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=markup)
        await update.callback_query.answer()
    else:
        await update.message.reply_text(message, reply_markup=markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "new_search":
        await query.edit_message_text("🔍 Type serial name:")
        return
    if data.startswith("page_"):
        parts = data.split("_")
        serial_name = parts[1]
        page = int(parts[2])
        await show_episodes(update, serial_name, page)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_serial))
    app.add_handler(CallbackQueryHandler(button_click))
    print("Bot running!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
