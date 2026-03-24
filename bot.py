import logging
import datetime
import random
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# --- Flask Server for Keep Alive ---
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot is Alive!"

def run():
    app_flask.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- আপনার অরিজিনাল বটের কোড শুরু ---
TOKEN = '8586079260:AAEILif880IasDnEyqTHfhzfwCsh1Ff0CxM'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_user_info(update: Update):
    user = update.effective_user
    name = user.first_name if user.first_name else "User"
    username = f"@{user.username}" if user.username else "Not Set"
    uid = user.id
    return name, username, uid

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name, _, _ = get_user_info(update)
    text = (f"⚡️Welcome {name} to Vanila exchange ! ⚡️\n"
            "Sell, Buy, and strike deals in seconds!!\n"
            "All transactions are secure and transparent.\n"
            "All types of cards are available here at best rates. Current rate is 33%")
    keyboard = [[InlineKeyboardButton("🛒Buy Cards", callback_data='buy_cards'), 
                 InlineKeyboardButton("💳 Stock", callback_data='stock')],
                [InlineKeyboardButton("📞 Contact Admin", url='https://t.me/Vanila_card_prepaid')]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name, username, uid = get_user_info(update)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ref_link = f"https://t.me/{(await context.bot.get_me()).username}?start={uid}"
    text = (f"⚡ VANILA PROFILE ⚡\n\n👤 {name}\n🆔 User ID: `{uid}`\n🔹 Username: {username}\n💰 TON Balance: 0.00\n"
            f"Last updated: {now}")
    await update.message.reply_text(text, parse_mode='Markdown')

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("⚡ vanilla prepaid — TON DEPOSIT ⚡\n\nDeposit Address:\n"
            "`UQBZSURuWZwh8BtakAknwG0wsbpzpTGBUDJNhx5Uun4Vhzah`\n\nMin: 9 TON")
    keyboard = [[InlineKeyboardButton("Confirm✅", callback_data='confirm_dep'), 
                 InlineKeyboardButton("Cancel⛔", callback_data='cancel_dep')]]
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'buy_cards':
        await query.message.reply_text("Insufficient balance.")
    elif query.data == 'confirm_dep':
        context.user_data['depositing'] = True
        await query.message.reply_text("Please enter the amount.......")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('depositing'):
        # আপনার ডিপোজিট লজিক এখানে থাকবে...
        await update.message.reply_text("Processing...")
        context.user_data.clear()

# --- মেইন রানার ---
if __name__ == '__main__':
    # ১. প্রথমে ওয়েব সার্ভারটি চালু করবে
    keep_alive()
    
    # ২. তারপর টেলিগ্রাম বট চালু হবে
    print("Starting Bot...")
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('profile', profile))
    app.add_handler(CommandHandler('deposit', deposit))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    app.run_polling()
