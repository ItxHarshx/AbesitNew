import html
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from wyr_questions import NORMAL, NSFW

# ---------------------------------------------------------------------------
# Mode registry — to add a new mode later:
#   1. add a question list to wyr_questions.py
#   2. add one entry here (label, emoji, command name, question list)
#   3. add one CommandHandler line in main.py pointing at a thin wrapper
#      (copy cmd_next / cmd_nsfw below and swap the mode key)
# ---------------------------------------------------------------------------
WYR_MODES = {
    "normal": {"label": "Normal", "emoji": "🤔", "command": "next", "questions": NORMAL},
    "nsfw": {"label": "18+", "emoji": "🔞", "command": "nsfw", "questions": NSFW},
}

MIN_VOTES_FOR_TIMER = 2
REVEAL_DELAY_SECONDS = 15

# In-memory state, one active game per chat. No DB — resets on restart.
# chat_id -> {
#   "mode": str, "option_a": str, "option_b": str,
#   "message_id": int, "votes": {user_id: "a"/"b"}, "names": {user_id: str},
#   "status": "voting" | "counting" | "revealed", "job": Job | None,
# }
wyr_games: dict[int, dict] = {}


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def _vote_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔵", callback_data="wyr_vote:a"),
        InlineKeyboardButton("🔴", callback_data="wyr_vote:b"),
    ]])


def _next_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Next question ➡️", callback_data="wyr_next")
    ]])


def _skip_keyboard(requested_mode: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("⏭ Skip Question", callback_data=f"wyr_skip:{requested_mode}")
    ]])


def _render_text(state: dict, result: dict | None = None) -> str:
    mode_cfg = WYR_MODES[state["mode"]]
    a, b = html.escape(state["option_a"]), html.escape(state["option_b"])
    lines = [
        f"<b>{mode_cfg['emoji']} Would You Rather...</b> <i>({mode_cfg['label']})</i>",
        "",
    ]

    if result is None:
        lines.append(f"🔵 {a}")
        lines.append(f"🔴 {b}")
        lines.append("")
        if state["votes"]:
            if state["status"] == "counting":
                lines.append(f"<i>⏱ Revealing results in {REVEAL_DELAY_SECONDS}s...</i>")
            else:
                lines.append("<i>Waiting for players to answer...</i>")
            voted_names = ", ".join(html.escape(n) for n in state["names"].values())
            lines.append(f"✅ {voted_names} already answered!")
        else:
            lines.append("<i>Waiting for players to answer...</i>")
    else:
        lines.append(f"({result['pct_a']}%) 🔵 {a}")
        lines.append(f"({result['pct_b']}%) 🔴 {b}")
        lines.append("")
        for uid, choice in state["votes"].items():
            emoji = "🔵" if choice == "a" else "🔴"
            name = html.escape(state["names"].get(uid, "Someone"))
            lines.append(f"{emoji} {name}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core game flow
# ---------------------------------------------------------------------------
async def _post_question(chat_id: int, mode: str, context: ContextTypes.DEFAULT_TYPE,
                          edit_message_id: int | None = None):
    a, b = random.choice(WYR_MODES[mode]["questions"])
    state = {
        "mode": mode,
        "option_a": a,
        "option_b": b,
        "votes": {},
        "names": {},
        "status": "voting",
        "job": None,
        "message_id": edit_message_id,
    }
    text = _render_text(state)

    if edit_message_id:
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=edit_message_id,
            text=text, parse_mode="HTML", reply_markup=_vote_keyboard()
        )
    else:
        msg = await context.bot.send_message(
            chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=_vote_keyboard()
        )
        state["message_id"] = msg.message_id

    wyr_games[chat_id] = state


async def _finalize(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    state = wyr_games.get(chat_id)
    if not state:
        return

    total = len(state["votes"])
    a_votes = sum(1 for c in state["votes"].values() if c == "a")
    pct_a = round((a_votes / total) * 100) if total else 0
    pct_b = 100 - pct_a if total else 0
    result = {"total": total, "pct_a": pct_a, "pct_b": pct_b}

    state["status"] = "revealed"
    text = _render_text(state, result=result)

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=state["message_id"],
            text=text, parse_mode="HTML", reply_markup=_next_keyboard()
        )
    except Exception:
        pass


async def _reveal_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    state = wyr_games.get(chat_id)
    if not state or state["status"] != "counting":
        return  # game was skipped/cleared before the timer fired
    await _finalize(chat_id, context)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
async def _start_game(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str):
    chat = update.effective_chat

    if chat.type == "private":
        await update.message.reply_text(
            "This command only works inside the group, not in my DM."
        )
        return

    chat_id = chat.id
    existing = wyr_games.get(chat_id)

    if existing and existing["status"] in ("voting", "counting"):
        await update.message.reply_text(
            "⚠️ There's already a question running in this group!",
            reply_markup=_skip_keyboard(mode)
        )
        return

    await _post_question(chat_id, mode, context)


async def cmd_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _start_game(update, context, "normal")


async def cmd_nsfw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _start_game(update, context, "nsfw")


async def cmd_wyr_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # The only WYR command allowed to work in DM too.
    mode_lines = "\n".join(
        f"• /{cfg['command']} — {cfg['label']} questions"
        for cfg in WYR_MODES.values()
    )
    text = (
        "<b>🤔 Would You Rather</b>\n\n"
        "A quick group voting game. Someone starts a question, members vote, "
        f"and once at least {MIN_VOTES_FOR_TIMER} people have voted a "
        f"{REVEAL_DELAY_SECONDS}-second countdown begins before results are revealed.\n\n"
        "<b>Start a question:</b>\n"
        f"{mode_lines}\n\n"
        "<b>How to play:</b>\n"
        "Tap 🔵 or 🔴 to vote — you can only vote once per question, but you can "
        "still vote while the countdown is running. Once results are shown, anyone "
        "can tap <b>Next question</b> to continue in the same mode.\n\n"
        "If a question is already running and someone tries to start a new one, "
        "I'll offer a <b>Skip Question</b> button to end it early instead."
    )
    await update.message.reply_html(text)


# ---------------------------------------------------------------------------
# Callback query handling
# ---------------------------------------------------------------------------
async def wyr_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_chat.id
    user = update.effective_user

    if data.startswith("wyr_vote:"):
        await _handle_vote(query, context, chat_id, user, data.split(":", 1)[1])
    elif data == "wyr_next":
        await _handle_next(query, context, chat_id)
    elif data.startswith("wyr_skip"):
        requested_mode = data.split(":", 1)[1] if ":" in data else None
        await _handle_skip(query, context, chat_id, requested_mode)


async def _handle_vote(query, context: ContextTypes.DEFAULT_TYPE, chat_id: int, user, choice: str):
    state = wyr_games.get(chat_id)

    if not state or state["status"] not in ("voting", "counting") \
            or state["message_id"] != query.message.message_id:
        await query.answer("This question is no longer active.", show_alert=True)
        return

    if user.id in state["votes"]:
        await query.answer("You already answered this question!", show_alert=True)
        return

    state["votes"][user.id] = choice
    state["names"][user.id] = user.first_name
    await query.answer()

    if len(state["votes"]) >= MIN_VOTES_FOR_TIMER and state["status"] == "voting":
        state["status"] = "counting"
        job_queue = context.application.job_queue
        state["job"] = job_queue.run_once(_reveal_job, REVEAL_DELAY_SECONDS, data=chat_id)

    text = _render_text(state)
    try:
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=_vote_keyboard())
    except Exception:
        pass


async def _handle_next(query, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    state = wyr_games.get(chat_id)
    if not state or state["status"] != "revealed":
        await query.answer()
        return

    await query.answer()
    await _post_question(chat_id, state["mode"], context)  # new message for the new question


async def _handle_skip(query, context: ContextTypes.DEFAULT_TYPE, chat_id: int, requested_mode: str | None = None):
    state = wyr_games.get(chat_id)
    if not state or state["status"] not in ("voting", "counting"):
        await query.answer("No active question to skip.", show_alert=True)
        return

    if state.get("job"):
        try:
            state["job"].schedule_removal()
        except Exception:
            pass

    await query.answer("Skipping current question...")
    mode = requested_mode if requested_mode in WYR_MODES else state["mode"]

    await _finalize(chat_id, context)
    await _post_question(chat_id, mode, context)  # new message for the auto-started next question

    # Clean up the "already a question running" notice this skip button was on.
    try:
        await query.message.delete()
    except Exception:
        pass
