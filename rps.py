from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


async def rps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>[✊] Stone Paper Scissors, mini game</b>\n"
        "A head-to-head game where players secretly choose Stone, Paper, or Scissors. "
        "Reveal your choices together to see who wins the round.\n\n"

        "<b>🕹️ How to play:</b>\n"
        "• choose <b>Stone ✊, Paper ✋, or Scissors ✌️</b>.\n"
        "• choices will reveal at the same time.\n\n"

        "<b>📜 Rules:</b>\n"
        "• ✊ Stone beats ✌️ Scissors.\n"
        "• ✋ Paper beats ✊ Stone.\n"
        "• ✌️ Scissors beats ✋ Paper.\n\n"

        "still figuring out how can i implement this as a multilayer game (3 and more players)\n\n"
        "<i>#under_dev</i>"
    )

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
  )
