from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

async def atlas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "**[🌍] Atlas..., mini game**\n"
        "A fast-paced word chain game where each player names a place that starts with the last letter of the previous place.\n\n"
        "**🕹️ How to play:**\n"
        "One player starts by sending the name of any **city, state, country, river, mountain, island, or other geographical location**.\n"
        "The next player must reply with a place whose **first letter matches the last letter** of the previous place.\n\n"
        "**📜 Rules:**\n"
        "- No repeated place names.\n"
        "- Spellings must be correct.\n"
        "- Anyone who can't answer within the agreed time is eliminated.\n"
        "Last player remaining wins! 🏆\n\n"
      "<i> #under_dev</i>"
    )

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN
    )
