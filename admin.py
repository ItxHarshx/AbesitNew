from telegram import Update
from telegram.ext import ContextTypes

async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type == "private":
        await update.message.reply_text(
            "This command can only be used in a group."
        )
        return

    me = await chat.get_member(context.bot.id)

    if me.status not in ("administrator", "creator") or not me.can_promote_members:
        await update.message.reply_text(
            "❌ I need the 'Add New Admins' permission."
        )
        return

    sender = await chat.get_member(update.effective_user.id)

    if sender.status not in ("administrator", "creator") or (
        sender.status != "creator" and not sender.can_promote_members
    ):
        await update.message.reply_text(
            "❌ You need the 'Add New Admins' permission."
        )
        return

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    elif context.args:
        try:
            target = await context.bot.get_chat(int(context.args[0]))
        except:
            await update.message.reply_text(
                "Invalid user ID."
            )
            return

    else:
        await update.message.reply_text(
            "Reply to a user's message or use:\n"
            "/promote <user_id>"
        )
        return

    member = await chat.get_member(target.id)

    if member.status == "creator":
        await update.message.reply_text(
            "You cannot promote the group owner."
        )
        return

    if member.status == "administrator":
        await update.message.reply_text(
            "User is already an admin."
        )
        return

    if target.id == context.bot.id:
        await update.message.reply_text(
            "I am already an admin."
        )
        return

    await context.bot.promote_chat_member(
        chat_id=chat.id,
        user_id=target.id,
        can_delete_messages=True,
        can_pin_messages=True,
        can_manage_video_chats=False,
        can_restrict_members=False,
        can_change_info=False,
        can_invite_users=False,
        can_promote_members=False,
        can_manage_topics=False,
        can_post_messages=False,
        can_edit_messages=False,
        is_anonymous=False,
    )

    await update.message.reply_html(
        f"👮 <b>User Promoted</b>\n\n"
        f"👤 User: {target.mention_html()}\n"
        f"🛡️ By: {update.effective_user.mention_html()}"
    )


async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type == "private":
        await update.message.reply_text(
            "This command can only be used in a group."
        )
        return

    me = await chat.get_member(context.bot.id)

    if me.status not in ("administrator", "creator") or not me.can_promote_members:
        await update.message.reply_text(
            "❌ I need the 'Add New Admins' permission."
        )
        return

    sender = await chat.get_member(update.effective_user.id)

    if sender.status not in ("administrator", "creator") or (
        sender.status != "creator" and not sender.can_promote_members
    ):
        await update.message.reply_text(
            "❌ You need the 'Add New Admins' permission."
        )
        return

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    elif context.args:
        try:
            target = await context.bot.get_chat(int(context.args[0]))
        except:
            await update.message.reply_text(
                "Invalid user ID."
            )
            return
        
    else:
      await update.message.reply_text(
        "Reply to a user's message or use:\n"
        "/demote <user_id>"
      )
      return

    member = await chat.get_member(target.id)

    if member.status == "creator":
        await update.message.reply_text(
            "You cannot demote the group owner."
        )
        return

    if member.status != "administrator":
        await update.message.reply_text(
            "User is not an admin."
        )
        return

    if target.id == context.bot.id:
        await update.message.reply_text(
            "I cannot demote myself."
        )
        return

    await context.bot.promote_chat_member(
        chat_id=chat.id,
        user_id=target.id,
        can_delete_messages=False,
        can_pin_messages=False,
        can_manage_video_chats=False,
        can_restrict_members=False,
        can_change_info=False,
        can_invite_users=False,
        can_promote_members=False,
        can_manage_topics=False,
        can_post_messages=False,
        can_edit_messages=False,
        is_anonymous=False,
    )

    await update.message.reply_html(
        f"⬇️ <b>User Demoted</b>\n\n"
        f"👤 User: {target.mention_html()}\n"
        f"🛡️ By: {update.effective_user.mention_html()}"
  )
