from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


async def atlas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>[🌍] Atlas..., mini game</b>\n"
        "A fast-paced word chain game where each player names a place that starts with the last letter of the previous place.\n\n"

        "<b>🕹️ How to play:</b>\n"
        "One player starts by sending the name of any <b>city, state, country, river, mountain, island, or other geographical location</b>.\n"
        "The next player must reply with a place whose <b>first letter matches the last letter</b> of the previous place.\n\n"

        "<b>📜 Rules:</b>\n"
        "• No repeated place names.\n"
        "• Spellings must be correct.\n"
        "• Anyone who can't answer within the agreed time is eliminated.\n\n"

        "Last player remaining wins! 🏆\n\n"
        "<i>#under_dev</i>"
    )

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
