from dotenv import load_dotenv
from telegram import Update
from telegram.ext import MessageHandler, filters
import asyncio
from telegram.ext import Application, CommandHandler, ContextTypes
import os
from info import SUDO_USERS, GROUP_ID
import time
from datetime import datetime

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
GROUP_LOCKED = False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mention = update.effective_user.mention_html(
        update.effective_user.first_name
    )
    bot = await context.bot.get_me()

    text = (
    f'➻ Hey <b>{mention}</b>, This is <a href="tg://user?id={bot.id}"><b>{context.bot.first_name}</b></a>, Your Abesit assistant.'
    )

    await update.message.reply_html(text)
    
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
    MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
    )
    app.add_handler(CommandHandler("pin", pin))
    app.add_handler(CommandHandler("unpin", unpin))
    app.add_handler(CommandHandler("announce", announce))
    app.add_handler(CommandHandler("lockgroup", lockgroup))
    app.add_handler(CommandHandler("unlockgroup", unlockgroup))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("lockstatus", lockstatus))
    app.add_handler(CommandHandler("sudoers", sudoers))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(
    MessageHandler(
        filters.ALL & ~filters.COMMAND,
        enforce_group_lock
    )
    )

    print("Bot is running...")

    app.run_polling()

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:

        mention = user.mention_html(user.first_name)

        msg = await update.message.reply_html(
            f"Hello {mention}, welcome to ABESIT Batch (2026-2027). wishing you a great college journey! 🎉"
        )

        await asyncio.sleep(300)  # 5 minutes

        try:
            await msg.delete()
        except:
            pass

async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    member = await chat.get_member(user.id)

    if member.status not in ["administrator", "creator"]:
        return

    if not update.message.reply_to_message:
        msg = await update.message.reply_text(
            "Reply to a message to pin it."
        )

        await asyncio.sleep(5)

        try:
            await msg.delete()
        except:
            pass

        return

    await update.message.reply_to_message.pin(
        disable_notification=True
    )

    msg = await update.message.reply_text(
        "Message pinned."
    )

    await asyncio.sleep(5)

    try:
        await msg.delete()
    except:
        pass

async def unpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    member = await chat.get_member(user.id)

    if member.status not in ["administrator", "creator"]:
        return

    await chat.unpin_all_messages()

    msg = await update.message.reply_text(
        "Message unpinned."
    )

    await asyncio.sleep(5)

    try:
        await msg.delete()
    except:
        pass

async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Sudo check
    # Sudo check
    if user_id not in SUDO_USERS:
        await update.message.reply_text(
        "Only official admins are allowed to make announcements."
    )
        return

    # DM only
    if update.effective_chat.type != "private":
        await update.effective_chat.send_message(
        "Announcements can only be made from my DM."
    )
        return

    # Message check
    if not context.args:
        await update.message.reply_text(
            "Usage:\n/announce Your announcement here"
        )
        return

    announcement = " ".join(context.args)

    msg = await context.bot.send_message(
        chat_id=GROUP_ID,
    text=(
        "<b>📢 ANNOUNCEMENT !</b>\n\n"
        f"{announcement}\n\n"
        "<b>- ABESIT Assistant.</b>"
    ),
    parse_mode="HTML"
        )

    await msg.pin(disable_notification=True)

    await update.message.reply_text(
        "Announcement posted and pinned."
    )


async def lockgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GROUP_LOCKED
    
    if GROUP_LOCKED:
        await update.message.reply_text(
        "🔒 Group is already locked."
    )
        return

    user_id = update.effective_user.id

    if user_id not in SUDO_USERS:
        await update.message.reply_text(
            "Only official admins can use this command."
        )
        return

    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "This command can only be used in a group."
        )
        return

    GROUP_LOCKED = True

    await update.message.reply_text(
        "🔒 Group Lock Enabled\n\n"
        "Only group admins can send messages until the group is unlocked."
    )
    
async def unlockgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GROUP_LOCKED
    
    if not GROUP_LOCKED:
        await update.message.reply_text(
        "🔓 Group is already unlocked."
    )
        return

    user_id = update.effective_user.id

    if user_id not in SUDO_USERS:
        await update.message.reply_text(
            "Only official admins can use this command."
        )
        return

    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "This command can only be used in a group."
        )
        return

    GROUP_LOCKED = False

    await update.message.reply_text(
        "🔓 Group Lock Disabled\n\n"
        "Members can send messages again."
    )
    
async def enforce_group_lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GROUP_LOCKED

    if not update.effective_user:
        return

    if update.effective_chat.type == "private":
        return

    if not GROUP_LOCKED:
        return

    user = update.effective_user
    chat = update.effective_chat

    member = await chat.get_member(user.id)

    if member.status in ["administrator", "creator"]:
        return

    if update.message:
        try:
            await update.message.delete()
        except Exception as e:
            print(f"DELETE ERROR: {e}")


            
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.perf_counter()

    msg = await update.message.reply_text("🏓 Pinging...")

    response_time = (time.perf_counter() - start_time) * 1000

    latency = response_time
    
    await msg.edit_text(
        f"🏓 Pong!\n\n"
        f"⚡ Latency: {latency:.0f} ms\n"
        f"⏱ Response Time: {response_time:.0f} ms\n\n"
        f"🤖 Status: Online"
    )


async def lockstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "This command can only be used in a group."
        )
        return

    if GROUP_LOCKED:
        await update.message.reply_text(
            "🔒 Group Status: Locked\n\n"
            "Only group admins can send messages."
        )
    else:
        await update.message.reply_text(
            "🔓 Group Status: Unlocked\n\n"
            "All members can send messages."
        )

async def sudoers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "<b>Official Admins !</b>\n\n"

    for user_id in SUDO_USERS:
        try:
            user = await context.bot.get_chat(user_id)

            text += (
                f'• <a href="tg://user?id={user_id}">'
                f'{user.first_name}</a>\n'
            )

        except:
            text += f"• <code>{user_id}</code>\n"

    await update.message.reply_html(text)



# ---------- helper: check admin ----------
async def is_admin(chat, user_id):
    member = await chat.get_member(user_id)
    return member.status in ["administrator", "creator"] and member.can_restrict_members


# ---------- helper: resolve target ----------
async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat = update.effective_chat

    # 1. Reply case
    if message.reply_to_message:
        return message.reply_to_message.from_user

    # 2. Argument case
    if context.args:
        arg = context.args[0]

        # Case A: numeric ID
        if arg.isdigit():
            try:
                return await context.bot.get_chat(int(arg))
            except:
                return None

        # Case B: username (@user or user)
        if arg.startswith("@"):
            arg = arg[1:]

        try:
            return await context.bot.get_chat(arg)
        except:
            return None

    return None


# ---------- kick command ----------
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Only works in groups.")
        return

    # admin check
    if not await is_admin(chat, user.id):
        await update.message.reply_text("❌ You don't have permission to kick users.")
        return

    target = await get_target_user(update, context)

    if not target:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "/kick (reply)\n"
            "/kick user_id\n"
            "/kick @username"
        )
        return

    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # kick (ban + unban)
        await chat.ban_member(target.id)
        await chat.unban_member(target.id)

        admin_name = user.first_name

        await update.message.reply_text(
            f"👢 {target.first_name} was kicked by {admin_name}\n"
            f"📝 Reason: {reason}"
        )

        log_text = (
            f"🚨 KICK ACTION\n\n"
            f"👤 User: {target.first_name} ({target.id})\n"
            f"👮 Admin: {admin_name} ({user.id})\n"
            f"🏠 Group: {chat.title}\n"
            f"🕒 Time: {time_now}\n"
            f"📌 Reason: {reason}"
        )

        # send to sudoers
        for sudo_id in SUDO_USERS:
            try:
                await context.bot.send_message(sudo_id, log_text)
            except:
                pass

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")





if __name__ == "__main__":
    main()
