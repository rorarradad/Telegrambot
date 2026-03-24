import logging
import datetime
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8586079260:AAEILif880IasDnEyqTHfhzfwCsh1Ff0CxM')

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

    keyboard = [
        [InlineKeyboardButton("🛒Buy Cards", callback_data='buy_cards'),
         InlineKeyboardButton("💳 Stock", callback_data='stock')],
        [InlineKeyboardButton("📞 Contact Admin", url='https://t.me/Vanila_card_prepaid')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name, username, uid = get_user_info(update)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ref_link = f"https://t.me/{(await context.bot.get_me()).username}?start={uid}"

    text = (f"⚡ VANILA PROFILE ⚡\n\n"
            f"👤 {name}\n"
            f"🧠 \"It is impossible to love and to be wise.\"\n"
            f"💬 By: Francis Bacon\n\n"
            f"🆔 User ID: `{uid}`\n"
            f"🔹 Username: {username}\n"
            f"💰 TON Balance: 0.0000000000\n"
            f"💵 USD Total: $0.00\n\n"
            f"📥 Deposits\n• Total: 0.0000 TON\n• USD: $0.00\n• Last: Never\n\n"
            f"🛒 Purchases\n• Count: 0\n• USD Spent: $0.00\n• Last Cards:\n  • No cards purchased yet.\n\n"
            f"👥 Referrals\n• Invited: 0\n• Referred By: `{ref_link}`\n\n"
            f"🛠 Permissions\n• Vendor: ❌\n• Re-list: ❌\n\n"
            f"Last updated: {now}")
    await update.message.reply_text(text, parse_mode='Markdown')

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _, _, uid = get_user_info(update)
    ref_link = f"https://t.me/{(await context.bot.get_me()).username}?start={uid}"
    text = (f"🎉 REFERRAL PROGRAM\n\n"
            f"Invite friends and earn $1.00 for each active referral!\n\n"
            f"🔗 Your unique link: `{ref_link}`\n\n"
            f"📊 Stats\n• Total referrals: 0\n• Earned: $0.00\n\n"
            f"❗ Rules\n- Bonus awarded when referral completes first transaction\n"
            f"- No self-referrals\n- Fraudulent referrals will be banned")
    await update.message.reply_text(text, parse_mode='Markdown')

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("⚡ vanilla prepaid — TON DEPOSIT ⚡\n\n"
            "Deposit Information:\n"
            "`UQBZSURuWZwh8BtakAknwG0wsbpzpTGBUDJNhx5Uun4Vhzah` (ট্যাপ করলে কপি হবে)\n\n"
            "Minimum Deposit: 9 TON\n"
            "Instructions:\n"
            "1. Send your deposit to the address above.\n"
            "2. Wait for 1 confirmation.\n"
            "3. Your balance will update automatically.\n"
            "4. Please remember to send TON only through the TON Network. ✅\n\n"
            "⚠️ WARNING:\n- Deposits below the minimum amount will not be processed.\n"
            "- This address is valid only for your account. Do not share it.\n\n"
            "⚠️ Note: This deposit session is only active for 30 minutes. Please send your deposit before it expires.")

    keyboard = [[InlineKeyboardButton("Confirm✅", callback_data='confirm_dep'),
                 InlineKeyboardButton("Cancel⛔", callback_data='cancel_dep')]]
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'buy_cards':
        await query.message.reply_text("You do not have sufficient balance. Please deposit first. To deposit, please click the deposit option")
    elif query.data == 'stock':
        await query.message.reply_text("Due to insufficient balance, you cannot view the Stock.")
    elif query.data == 'confirm_dep':
        context.user_data['depositing'] = True
        await query.message.reply_text("Please enter the amount.......")
    elif query.data == 'cancel_dep':
        await query.message.reply_text("Deposit cancelled.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text

    if context.user_data.get('depositing'):
        if not context.user_data.get('amount_received'):
            try:
                amount = float(msg)
                if amount < 9:
                    await update.message.reply_text("Minimum deposit is 9 TON. Please enter the correct amount")
                else:
                    context.user_data['amount_received'] = amount
                    await update.message.reply_text("Submit withdraw Txid :")
            except ValueError:
                await update.message.reply_text("Please enter a valid number.")
        else:
            txid = msg
            amount = context.user_data['amount_received']
            name, _, _ = get_user_info(update)
            order_no = random.randint(51, 159)
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            receipt = (f"NAME : {name}\n"
                       f"AMOUNT: {amount}\n"
                       f"Txid : {txid}\n"
                       f"Order Number : `{order_no}`\n"
                       f"TIME : {now}\n"
                       f"NOTE : Balance will be added within 1/2 minutes. If not added, contact customer care.")

            await update.message.reply_text(receipt, parse_mode='Markdown')
            context.user_data.clear()

async def listings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Due to insufficient balance, you cannot view the list.")

async def unreg_listings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Due to insufficient balance, you cannot view the unregistered list")

async def cents_listings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Due to insufficient balance, you cannot view the cents list .")

async def list_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Due to insufficient balance, you cannot view the list .")

async def list_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Due to insufficient balance, you cannot view the listing range .")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Your current balance: 0.00 TON")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Insufficient balance in your account. Minimum withdrawal is 0.1 TON. Current balance: 0.00 TON")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("If you need help, please contact the support bot @Vanila_card_prepaid")

async def refund_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("⚡️⚡️⚡️ VERY IMPORTANT ⚡️⚡️⚡️\n💳 VANILA Exchange – Refund Policy 💳\n\n"
            "📢 Please read this carefully to avoid refund rejection.\n\n"
            "✅✅✅ CARD REFUND REQUIREMENTS ✅✅✅\n"
            "1️⃣ Refund requests must be submitted within 25 minutes of purchase.\n"
            "2️⃣ Refunds are accepted ONLY if the card is stolen or partially used.\n"
            "3️⃣ When reporting a stolen card, you must clearly state the stolen amount.\n"
            "4️⃣ You must have a valid Telegram username set.\n"
            "5️⃣ 🔁 Do NOT recheck the card balance multiple times.\n\n"
            "💬 Official Refund Support: @vanilarefund\n\n"
            "❌❌❌ AUTOMATIC REFUND REJECTIONS ❌❌❌\n"
            "🚫 No refund for ReListed cards\n🚫 No refund for cards used with Google / Google Pay\n"
            "📩 Need help? Contact support: https://t.me/vanilarefund")
    await update.message.reply_text(text)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('profile', profile))
    app.add_handler(CommandHandler('ref', referral))
    app.add_handler(CommandHandler('deposit', deposit))
    app.add_handler(CommandHandler('listings', listings))
    app.add_handler(CommandHandler('unregistered_listing', unreg_listings))
    app.add_handler(CommandHandler('cents_listing', cents_listings))
    app.add_handler(CommandHandler('listing_filter', list_filter))
    app.add_handler(CommandHandler('listing_range', list_range))
    app.add_handler(CommandHandler('balance', balance))
    app.add_handler(CommandHandler('withdraw', withdraw))
    app.add_handler(CommandHandler('help', help_cmd))
    app.add_handler(CommandHandler('refund_rules', refund_rules))

    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot is running...")
    app.run_polling()
