import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from solana.rpc.api import Client

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
TELEGRAM_BOT_TOKEN = '7715709190:AAEkgrVVdvNL_Wp90oLep7EBnBFrkrBygzs'

# Solana API client
solana_client = Client("https://api.mainnet-beta.solana.com")

# Dictionary to store wallet addresses
user_wallets = {}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Use /addwallet to add a Solana wallet.")

def add_wallet(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Please send the Solana wallet address you want to add.")

def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    wallet_address = update.message.text.strip()

    if wallet_address not in user_wallets.get(user_id, []):
        if user_id not in user_wallets:
            user_wallets[user_id] = []
        user_wallets[user_id].append(wallet_address)
        update.message.reply_text(f"Wallet {wallet_address} added!")
    else:
        update.message.reply_text(f"Wallet {wallet_address} is already added.")

def balance(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id in user_wallets and user_wallets[user_id]:
        keyboard = [[InlineKeyboardButton(wallet, callback_data=wallet) for wallet in user_wallets[user_id]]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Choose a wallet to check balance:", reply_markup=reply_markup)
    else:
        update.message.reply_text("You have no wallets added. Use /addwallet to add one.")

def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    wallet_address = query.data

    try:
        balance = solana_client.get_balance(wallet_address)
        balance_amount = balance['result']['value'] / 10**9  # Convert lamports to SOL
        query.edit_message_text(text=f"Balance of {wallet_address}: {balance_amount:.4f} SOL")
    except Exception as e:
        query.edit_message_text(text=f"Error retrieving balance: {e}")

def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # Register handlers
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('addwallet', add_wallet))
    updater.dispatcher.add_handler(CommandHandler('balance', balance))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.dispatcher.add_handler(CallbackQueryHandler(button_callback))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
