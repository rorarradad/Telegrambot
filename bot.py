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

def get_user_info(update: Update):
    user = update.effective_user
    name = user.first_name if user.first_name else "User"
    uid = user.id
    return name, uid

# --- কমান্ড ফাংশনসমূহ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name, _ = get_user_info(update)
    text = (f"⚡️Welcome {name} to Vanila exchange ! ⚡️\n"
            "Sell, Buy, and strike deals in seconds!!\n"
            "Current rate is 33%")
    keyboard = [[InlineKeyboardButton("🛒Buy Cards", callback_data='buy_cards'), 
                 InlineKeyboardButton("💳 Stock", callback_data='stock')],
                [InlineKeyboardButton("📞 Contact Admin", url='https://t.me/Vanila_card_prepaid')]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _, uid = get_user_info(update)
    bot_username = (await context.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={uid}"
    text = (f"🎉 **REFERRAL PROGRAM**\n\n"
            f"Invite friends and earn 5% every deposit each active referral!\n\n"
            f"🔗 Your unique link: `{ref_link}` (Click to copy)\n\n"
            f"📊 **Stats**\n• Total referrals: 0\n• Earned: $0.00\n\n"
            f"❗ **Rules**\n- Bonus awarded when referral completes first transaction\n"
            f"- No self-referrals\n- Fraudulent referrals will be banned")
    await update.message.reply_text(text, parse_mode='Markdown')

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Insufficient balance in your account. Minimum withdrawal is 0.1 TON. Current balance: 0.00 TON")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("If you need help, please contact the support bot @Vanila_card_prepaid")

async def refund_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "⚡️⚡️⚡️ **VERY IMPORTANT** ⚡️⚡️⚡️\n"
        "💳 **VANILA Exchange – Refund Policy** 💳\n\n"
        "📢 Please read this carefully to avoid refund rejection.\n\n"
        "✅✅✅ **CARD REFUND REQUIREMENTS** ✅✅✅\n\n"
        "1️⃣ Refund requests must be submitted within 25 minutes of purchase.\n"
        "2️⃣ Refunds are accepted ONLY if the card is stolen or partially used.\n"
        "3️⃣ When reporting a stolen card, you must clearly state the stolen amount.\n"
        "4️⃣ You must have a valid Telegram username set.\n"
        "5️⃣ 🔁 Do NOT recheck the card balance multiple times.\n\n"
        "💬 Official Refund Support: @vanilarefund\n\n"
        "❌❌❌ **AUTOMATIC REFUND REJECTIONS** ❌❌❌\n\n"
        "🚫 No refund for ReListed cards\n"
        "🚫 No refund for cards used with Google / Google Pay\n"
        "🚫 No Telegram username = Auto rejection\n"
        "🚫 No refund for Dead or Invalid cards\n\n"
        "📩 Need help? Contact support: https://t.me/vanilarefund"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("⚡ **vanilla prepaid — TON DEPOSIT** ⚡\n\n"
            "Deposit Information:\n"
            "`UQBZSURuWZwh8BtakAknwG0wsbpzpTGBUDJNhx5Uun4Vhzah` (Click to copy)\n\n"
            "Minimum Deposit: 9 TON\n\n"
            "Instructions:\n"
            "1. Send your deposit to the address above.\n"
            "2. Wait for 1 confirmation.\n"
            "4. Send TON only through the TON Network. ✅\n\n"
            "⚠️ Note: This deposit session is active for 30 minutes.")
    
    keyboard = [[InlineKeyboardButton("Confirm✅", callback_data='confirm_dep'), 
                 InlineKeyboardButton("Cancel⛔", callback_data='cancel_dep')]]
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

# --- বাটন ও মেসেজ লজিক ---

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirm_dep':
        context.user_data['step'] = 'waiting_amount'
        await query.message.reply_text("Please enter the amount.......")
    elif query.data == 'cancel_dep':
        await query.message.reply_text("Deposit cancelled.")
    elif query.data in ['buy_cards', 'stock']:
        await query.message.reply_text("Insufficient balance.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    user_step = context.user_data.get('step')

    if user_step == 'waiting_amount':
        try:
            amount = float(msg)
            if amount < 9:
                await update.message.reply_text("Minimum deposit is 9 TON. Please enter the correct amount")
            else:
                context.user_data['deposit_amount'] = amount
                context.user_data['step'] = 'waiting_txid'
                await update.message.reply_text("Submit withdraw Txid :")
        except ValueError:
            await update.message.reply_text("Please enter a valid number (e.g. 9 or 10.5)")

    elif user_step == 'waiting_txid':
        txid = msg
        amount = context.user_data.get('deposit_amount')
        name, _ = get_user_info(update)
        order_no = random.randint(51, 159)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        receipt = (f"NAME : {name}\n"
                   f"AMOUNT: {amount}\n"
                   f"Txid : {txid}\n"
                   f"Order Number : `{order_no}` (Click to copy)\n"
                   f"TIME : {now}\n"
                   f"NOTE : Balance will be added within 1/2 minutes. If not added, contact customer care.")
        
        await update.message.reply_text(receipt, parse_mode='Markdown')
        context.user_data.clear()

async def common_no_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Due to insufficient balance, you cannot access this feature.")

# --- মেইন রানার ---
if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()
    
    # কমান্ড হ্যান্ডলারসমূহ
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('ref', referral))
    app.add_handler(CommandHandler('withdraw', withdraw))
    app.add_handler(CommandHandler('refund_rules', refund_rules))
    app.add_handler(CommandHandler('help', help_cmd))
    app.add_handler(CommandHandler('deposit', deposit))
    app.add_handler(CommandHandler(['listings', 'profile', 'balance'], start)) # এগুলোও স্টার্ট বা প্রোফাইলে পাঠাতে পারেন
    
    # বাটন ও টেক্সট হ্যান্ডলার
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is updating with new features...")
    app.run_polling()
                
