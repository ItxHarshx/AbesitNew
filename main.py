import re
import time
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters, Application, CommandHandler, ContextTypes
from info import SUDO_USERS, GROUP_ID

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
GROUP_LOCKED = False
ANTILINK_ENABLED = False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mention = update.effective_user.mention_html(
        update.effective_user.first_name
    )
    bot = await context.bot.get_me()

    if update.effective_chat.type == "private":
        text = (
            f'👋 Hey <b>{mention}</b>!\n\n'
            f'I am <a href="tg://user?id={bot.id}"><b>{context.bot.first_name}</b></a>, your ABESIT assistant.\n\n'
            f'📌 Use /help to explore my features.'
        )
else:
    text = (
        f'👋 Hey <b>{mention}</b>!\n\n'
        f'I am <a href="tg://user?id={bot.id}"><b>{context.bot.first_name}</b></a>.\n\n'
        f'📌 Use /help in my DM to explore my features.'
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🤖 Open Bot",
                url=f"https://t.me/{bot.username}?start=start"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_html(
        text,
        reply_markup=reply_markup
    )
    return

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
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("antilink", antilink))

    app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, anti_link_filter)
    )
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

        await update.message.reply_html(
            f"Hello {mention}, welcome to ABESIT Batch (2026-2027). Wishing you a great college journey! 🎉"
        )
        
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



async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    admin = update.effective_user

    # Group only
    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text("This command can only be used in the group.")
        return

    # Admin check
    admin_member = await chat.get_member(admin.id)

    if (
        admin_member.status != "creator"
        and not getattr(admin_member, "can_restrict_members", False)
    ):
        await update.message.reply_text(
            "❌ You are missing the required rights (Ban Users)."
        )
        return

    target = None
    reason = "No reason provided"

    # Reply method
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

        if context.args:
            reason = " ".join(context.args)

    # ID method
    elif context.args:
        arg = context.args[0]

        if arg.isdigit():
            try:
                member = await chat.get_member(int(arg))
                target = member.user
            except Exception:
                await update.message.reply_text(
                    "User not found in this group."
                )
                return

            if len(context.args) > 1:
                reason = " ".join(context.args[1:])

        else:
            await update.message.reply_text(
                "⚠️ Username-based kicking is not reliable through the Telegram Bot API.\n\n"
                "Use:\n"
                "• Reply to a user's message\n"
                "• /kick <user_id>"
            )
            return

    else:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "• Reply to a user: /kick reason\n"
            "• /kick <user_id> reason"
        )
        return

    # Prevent kicking admins
    try:
        target_member = await chat.get_member(target.id)

        if target_member.status in ("administrator", "creator"):
            await update.message.reply_text(
                "❌ I can't kick administrators."
            )
            return
    except Exception:
        pass

    try:
        await context.bot.ban_chat_member(
            chat_id=chat.id,
            user_id=target.id
        )

        await asyncio.sleep(1.5)

        await context.bot.unban_chat_member(
            chat_id=chat.id,
            user_id=target.id,
            only_if_banned=True
        )

        target_mention = (
    f'<a href="tg://user?id={target.id}">'
    f'{target.first_name}</a>'
)
        admin_mention = (
    f'<a href="tg://user?id={admin.id}">'
    f'{admin.first_name}</a>'
)
        await update.message.reply_html(
            f"{target_mention} kicked by {admin_mention}.\n"
            f"📝 Reason: {reason}"
        )

        log_text = (
            f"🚨 <u><b>KICK ACTION</b></u>\n\n"
            f"<b>• User:</b> {target_mention} (<code>{target.id}</code>)\n"
            f"<b>• Kicked By:</b> {admin_mention}\n"
            f"<b>• At:</b> <i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>\n"
            f"<b>• Reason:</b> {reason}"
        )

        for sudo_id in SUDO_USERS:
            try:
                await context.bot.send_message(
                    chat_id=sudo_id,
                    text=log_text,
                    parse_mode="HTML"
                )
            except Exception:
                pass

    except Exception as e:
        await update.message.reply_text(
            f"❌ Failed to kick user:\n{e}"
        )

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    admin = update.effective_user

    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text(
            "This command can only be used in the group."
        )
        return

    admin_member = await chat.get_member(admin.id)

    if (
        admin_member.status != "creator"
        and not getattr(admin_member, "can_restrict_members", False)
    ):
        await update.message.reply_text(
            "❌ You are missing the required rights (Ban Users)."
        )
        return

    target = None
    reason = "No reason provided"

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

        if context.args:
            reason = " ".join(context.args)

    elif context.args and context.args[0].isdigit():
        try:
            member = await chat.get_member(int(context.args[0]))
            target = member.user
        except Exception:
            await update.message.reply_text(
                "User not found in this group."
            )
            return

        if len(context.args) > 1:
            reason = " ".join(context.args[1:])

    else:
        await update.message.reply_text(
            "Usage:\n"
            "• Reply to a user: /ban reason\n"
            "• /ban <user_id> reason"
        )
        return

    try:
        member = await chat.get_member(target.id)

        if member.status in ("administrator", "creator"):
            await update.message.reply_text(
                "❌ I can't ban administrators."
            )
            return
    except Exception:
        pass
        
    try:
        member = await chat.get_member(target.id)
        
        if member.status == "kicked":
            await update.message.reply_html(
                f"❌ {target.mention_html()} is already banned."
            )
            return
    except Exception:
        pass
    
    try:
        await context.bot.ban_chat_member(
            chat_id=chat.id,
            user_id=target.id
        )

        await update.message.reply_html(
            f"🔨 {target.mention_html()} banned by "
            f"{admin.mention_html()}.\n"
            f"📝 Reason: {reason}"
        )

        log_text = (
            f"🚨 <u><b>BAN ACTION</b></u>\n\n"
            f"<b>• User:</b> {target.mention_html()} (<code>{target.id}</code>)\n"
            f"<b>• Banned By:</b> {admin.mention_html()}\n"
            f"<b>• At:</b> <i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>\n"
            f"<b>• Reason:</b> {reason}"
        )

        for sudo_id in SUDO_USERS:
            try:
                await context.bot.send_message(
                    chat_id=sudo_id,
                    text=log_text,
                    parse_mode="HTML"
                )
            except Exception:
                pass

    except Exception as e:
        await update.message.reply_text(
            f"❌ Failed to ban user:\n{e}"
        )

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    admin = update.effective_user

    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text(
            "This command can only be used in the group."
        )
        return

    admin_member = await chat.get_member(admin.id)

    if (
        admin_member.status != "creator"
        and not getattr(admin_member, "can_restrict_members", False)
    ):
        await update.message.reply_text(
            "❌ You are missing the required rights (Ban Users)."
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/unban <user_id>"
        )
        return

    user_id = context.args[0]

    if not user_id.isdigit():
        await update.message.reply_text(
            "User ID must be numeric."
        )
        return
        
    try:
        member = await chat.get_member(int(user_id))
        
        if member.status != "kicked":
            await update.message.reply_text(
                "❌ This user is not banned."
            )
            return
    except Exception:
        pass

    try:
        await context.bot.unban_chat_member(
            chat_id=chat.id,
            user_id=int(user_id)
        )

        await update.message.reply_html(
    f'User has been unbanned successfully.'
)

        log_text = (
            f"🚨 <u><b>UNBAN ACTION</b></u>\n\n"
            f"<b>• User ID:</b> <code>{user_id}</code>\n"
            f"<b>• Unbanned By:</b> {admin.mention_html()}\n"
            f"<b>• At:</b> <i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        )

        for sudo_id in SUDO_USERS:
            try:
                await context.bot.send_message(
                    chat_id=sudo_id,
                    text=log_text,
                    parse_mode="HTML"
                )
            except Exception:
                pass

    except Exception as e:
        await update.message.reply_text(
            f"❌ Failed to unban user:\n{e}"
        )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text(
            "This command can only be used in a group."
        )
        return

    member_count = await context.bot.get_chat_member_count(chat.id)

    admins = await chat.get_administrators()

    admin_count = len(admins)

    bot_count = sum(
        1 for member in admins
        if member.user.is_bot
    )

    sudo_count = len(SUDO_USERS)

    status = "Locked 🔒" if GROUP_LOCKED else "Unlocked 🔓"

    await update.message.reply_text(
        f"📊 Group Statistics.\n\n"
        f"•Total Members: {member_count}\n"
        f"• Admins: {admin_count}\n"
        f"• Bots: {bot_count}\n"
        f"• Official Admins: {sudo_count}\n\n"
        f"- Group Status: {status}"
    )

async def antilink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ANTILINK_ENABLED

    user_id = update.effective_user.id

    if user_id not in SUDO_USERS:
        await update.message.reply_text("You are not allowed to use this command. ")
        return

    if not context.args:
        status = "ON 🔒" if ANTILINK_ENABLED else "OFF 🔓"
        await update.message.reply_text(f"AntiLink Status: {status}")
        return

    arg = context.args[0].lower()

    if arg == "on":
        ANTILINK_ENABLED = True
        await update.message.reply_text("🚫 AntiLink Enabled")
    elif arg == "off":
        ANTILINK_ENABLED = False
        await update.message.reply_text("✅ AntiLink Disabled")
    else:
        await update.message.reply_text("Usage: /antilink on or off")


async def anti_link_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ANTILINK_ENABLED

    if not ANTILINK_ENABLED:
        return

    if update.effective_chat.type == "private":
        return

    if not update.message or not update.message.text:
        return

    user = update.effective_user
    chat = update.effective_chat

    # ignore admins
    member = await chat.get_member(user.id)
    if member.status in ("administrator", "creator"):
        return

    text = update.message.text.lower()

    # ONLY INVITE LINKS
    patterns = [
        # Telegram invite links
        r"t\.me/\+",
        r"t\.me/joinchat",
        r"tg://join\?invite",

        # WhatsApp group invites
        r"chat\.whatsapp\.com",

        # Instagram invite/share links (not reels/posts)
        r"instagram\.com/invites",
        r"instagram\.com/direct/invite",
        r"ig\.me/",
    ]
    for pattern in patterns:
        if re.search(pattern, text):
            try:
                await update.message.delete()

                warning = await context.bot.send_message(
                    chat_id=chat.id,
                    text=(
                        f"{user.mention_html()} 🚫 <b>AntiLink Detection is Enabled</b>\n"
                        "You can't send invite links in this group."
                    ),
                    parse_mode="HTML"
                )

                await asyncio.sleep(5)

                try:
                    await warning.delete()
                except Exception:
                    pass

            except Exception as e:
                print(f"ANTILINK ERROR: {e}")

            break
                    
        
if __name__ == "__main__":
    main()
