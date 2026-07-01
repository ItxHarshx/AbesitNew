import html
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from tord_questions import TRUTHS, DARES

# ---------------------------------------------------------------------------
# In-memory state, one active game per chat. No DB — resets on restart.
# chat_id -> {
#   "status": "lobby" | "started",
#   "creator_id": int, "creator_name": str,
#   "players": [{"id": int, "name": str}, ...],   # order = turn order
#   "turn_index": int,
#   "awaiting_choice": bool,
#   "choice_msg_id": int | None,
#   "closed": bool,
#   "lobby_job": Job | None,
#   "cancel_job": Job | None,
# }
# ---------------------------------------------------------------------------
tord_games: dict[int, dict] = {}

MIN_PLAYERS = 2
LOBBY_START_DELAY = 60      # once min players hit, auto-start after this
NO_JOIN_CANCEL_DELAY = 120  # cancel if nobody else joins within this


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _mention(user_id: int, name: str) -> str:
    return f'<a href="tg://user?id={user_id}">{html.escape(name)}</a>'


def _find_player(state: dict, user_id: int) -> int | None:
    for i, p in enumerate(state["players"]):
        if p["id"] == user_id:
            return i
    return None


async def _is_chat_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    return member.status in ("administrator", "creator")


async def _can_manage(update: Update, context: ContextTypes.DEFAULT_TYPE, state: dict) -> bool:
    user_id = update.effective_user.id
    if user_id == state["creator_id"]:
        return True
    if _find_player(state, user_id) is not None and await _is_chat_admin(update, context):
        return True
    return False


def _player_list_text(state: dict) -> str:
    lines = [f"{i + 1}. {_mention(p['id'], p['name'])}" for i, p in enumerate(state["players"])]
    return "\n".join(lines)


def _cancel_job(job):
    if job:
        try:
            job.schedule_removal()
        except Exception:
            pass


def _choice_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🤔 Truth", callback_data="tord_choice:truth"),
        InlineKeyboardButton("😈 Dare", callback_data="tord_choice:dare"),
    ]])


# ---------------------------------------------------------------------------
# /truthordare — info
# ---------------------------------------------------------------------------
async def cmd_truthordare_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>[🎭] Truth or Dare..., mini game</b>\n\n"
        "A simple truth or dare game — answer a truth or complete a dare, your choice.\n\n"
        "<b>🕹️ Game commands:</b>\n"
        "- /create_tord: start a new game\n"
        "- /join_tord: join the game\n"
        "- /leave_tord: leave the game\n"
        "- /start_tord: force starts (admin/creator)\n"
        "- /close_tord: stop new joins (admin/creator)\n"
        "- /cancel_tord: cancel the game (admin/creator)\n"
        "- /rm_tord: reply to remove a player (admin/creator)\n"
        "- /done: confirm your turn is finished\n\n"
        "<i> #under_dev </i>
    )
    await update.message.reply_html(text)


# ---------------------------------------------------------------------------
# /create_tord
# ---------------------------------------------------------------------------
async def cmd_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        await update.message.reply_text("This command only works inside the group.")
        return

    if chat.id in tord_games:
        await update.message.reply_text(
            "⚠️ There's already a running game in this group. Try /cancel_tord"
        )
        return

    state = {
        "status": "lobby",
        "creator_id": user.id,
        "creator_name": user.first_name,
        "players": [{"id": user.id, "name": user.first_name}],
        "turn_index": 0,
        "awaiting_choice": False,
        "choice_msg_id": None,
        "closed": False,
        "lobby_job": None,
        "cancel_job": None,
    }
    tord_games[chat.id] = state

    job_queue = context.application.job_queue
    state["cancel_job"] = job_queue.run_once(_no_join_cancel_job, NO_JOIN_CANCEL_DELAY, data=chat.id)

    await update.message.reply_html(
        "🎲 <b>Truth or Dare</b> game created by "
        f"{_mention(user.id, user.first_name)}!\n\n"
        f"<b>Players ({len(state['players'])}):</b>\n{_player_list_text(state)}\n\n"
        f"Need at least {MIN_PLAYERS} players. Use /join_tord to join!\n"
        f"⏳ Auto-cancels in 2 minutes if no one else joins."
    )


async def _no_join_cancel_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    state = tord_games.get(chat_id)
    if not state or state["status"] != "lobby" or len(state["players"]) >= MIN_PLAYERS:
        return
    del tord_games[chat_id]
    await context.bot.send_message(
        chat_id, "🛑 No one joined the Truth or Dare game in time. Game cancelled."
    )


# ---------------------------------------------------------------------------
# /join_tord
# ---------------------------------------------------------------------------
async def cmd_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    state = tord_games.get(chat.id)

    if not state:
        await update.message.reply_text("❌ No ongoing game in this chat. Try /create_tord")
        return

    if state["status"] == "started" and state["closed"]:
        await update.message.reply_text("🚫 This game is closed, no new players can join.")
        return

    if _find_player(state, user.id) is not None:
        await update.message.reply_text("You're already in this game!")
        return

    state["players"].append({"id": user.id, "name": user.first_name})

    if state["status"] == "lobby":
        if len(state["players"]) >= MIN_PLAYERS and state["lobby_job"] is None:
            _cancel_job(state["cancel_job"])
            state["cancel_job"] = None
            job_queue = context.application.job_queue
            state["lobby_job"] = job_queue.run_once(_lobby_start_job, LOBBY_START_DELAY, data=chat.id)
            await update.message.reply_html(
                f"{_mention(user.id, user.first_name)} joined!\n\n"
                f"<b>Players ({len(state['players'])}):</b>\n{_player_list_text(state)}\n\n"
                f"🕹️ Game starts in {LOBBY_START_DELAY}s — or /start_tord to begin now."
            )
        else:
            await update.message.reply_html(
                f"{_mention(user.id, user.first_name)} joined the game!\n\n"
                f"<b>Players ({len(state['players'])}):</b>\n{_player_list_text(state)}"
            )
    else:
        # joined mid-game — appended to end of turn order
        await update.message.reply_html(
            f"{_mention(user.id, user.first_name)} joined!\n\n"
        )

async def _lobby_start_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    state = tord_games.get(chat_id)
    if not state or state["status"] != "lobby":
        return
    await _begin_game(chat_id, context)


# ---------------------------------------------------------------------------
# /start_tord — skip lobby timer
# ---------------------------------------------------------------------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    state = tord_games.get(chat.id)

    if not state:
        await update.message.reply_text("❌ There's no game to start. Try /create_tord first")
        return

    if state["status"] == "started":
        await update.message.reply_text("⚠️ Game already started!")
        return

    if not await _can_manage(update, context, state):
        await update.message.reply_text("Only the game creator or a group admin can do that.")
        return

    if len(state["players"]) < MIN_PLAYERS:
        await update.message.reply_text(f"⚠️ Need at least {MIN_PLAYERS} players to start!")
        return

    _cancel_job(state["lobby_job"])
    _cancel_job(state["cancel_job"])
    state["lobby_job"] = None
    state["cancel_job"] = None
    await _begin_game(chat.id, context)


async def _begin_game(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    state = tord_games.get(chat_id)
    if not state:
        return
    state["status"] = "started"
    state["lobby_job"] = None
    state["cancel_job"] = None
    state["turn_index"] = 0

    await context.bot.send_message(
        chat_id,
        "🎮 <b>Game started!</b>\n\n<b>Turn order:</b>\n" + _player_list_text(state) + "\n\nLet's begin!",
        parse_mode="HTML",
    )
    await _post_turn(chat_id, context)


# ---------------------------------------------------------------------------
# Turn flow
# ---------------------------------------------------------------------------
async def _post_turn(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    state = tord_games.get(chat_id)
    if not state or not state["players"]:
        return

    state["turn_index"] %= len(state["players"])
    current = state["players"][state["turn_index"]]
    nxt = state["players"][(state["turn_index"] + 1) % len(state["players"])]
    state["awaiting_choice"] = True

    text = (
        f"🎯 {_mention(current['id'], current['name'])}, choose your fate!\n\n"
        f"<i>Next player: {_mention(nxt['id'], nxt['name'])}</i>"
    )
    msg = await context.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=_choice_keyboard())
    state["choice_msg_id"] = msg.message_id


async def tord_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = update.effective_chat.id
    user = update.effective_user
    state = tord_games.get(chat_id)

    if not state or state["status"] != "started" or not state["awaiting_choice"]:
        await query.answer("This round is no longer active.", show_alert=True)
        return

    current = state["players"][state["turn_index"]]
    if user.id != current["id"]:
        await query.answer("It's not your turn!", show_alert=True)
        return

    choice = query.data.split(":", 1)[1]
    state["awaiting_choice"] = False
    await query.answer()

    label = "Truth 🤔" if choice == "truth" else "Dare 😈"
    await query.edit_message_text(
        f"{_mention(current['id'], current['name'])} has chosen {label}.", parse_mode="HTML"
    )

    prompt = random.choice(TRUTHS if choice == "truth" else DARES)
    header = "🤔 Truth" if choice == "truth" else "😈 Dare"
    await context.bot.send_message(
        chat_id,
        f"{header} for {_mention(current['id'], current['name'])}:\n\n\"{html.escape(prompt)}\"\n\n"
        f"<i>(Other players can suggest their own truth/dare here too!)</i>\n"
        f"When done, use /done to move to the next player.",
        parse_mode="HTML",
    )


async def cmd_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    state = tord_games.get(chat.id)

    if not state or state["status"] != "started":
        await update.message.reply_text("❌ No ongoing game.")
        return

    current = state["players"][state["turn_index"]]
    if user.id != current["id"]:
        await update.message.reply_text("⏳ It's not your turn!")
        return

    state["turn_index"] = (state["turn_index"] + 1) % len(state["players"])
    await _post_turn(chat.id, context)


# ---------------------------------------------------------------------------
# /leave_tord
# ---------------------------------------------------------------------------
async def cmd_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    state = tord_games.get(chat.id)

    if not state:
        await update.message.reply_text("❌ No ongoing game to leave.")
        return

    idx = _find_player(state, user.id)
    if idx is None:
        await update.message.reply_text("You've not joined any game.")
        return

    await _remove_player(chat.id, context, idx, reason=f"{_mention(user.id, user.first_name)} left the game.")


# ---------------------------------------------------------------------------
# /rm_tord — reply-based
# ---------------------------------------------------------------------------
async def cmd_rm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    state = tord_games.get(chat.id)

    if not state:
        await update.message.reply_text("No game running!")
        return

    if not await _can_manage(update, context, state):
        await update.message.reply_text("Only the game creator or a group admin in the game can do that.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to the player's message with /rm_tord to remove them.")
        return

    target = update.message.reply_to_message.from_user
    idx = _find_player(state, target.id)
    if idx is None:
        await update.message.reply_text("This player not playing")
        return

    await _remove_player(
        chat.id, context, idx,
        reason=f"👢 {_mention(target.id, target.first_name)} has been removed from the game."
    )


async def _remove_player(chat_id: int, context: ContextTypes.DEFAULT_TYPE, idx: int, reason: str):
    state = tord_games.get(chat_id)
    if not state:
        return

    removed = state["players"].pop(idx)
    was_current_turn = state["status"] == "started" and state["awaiting_choice"] and idx == state["turn_index"]

    if state["status"] == "lobby":
        await context.bot.send_message(chat_id, reason, parse_mode="HTML")
        if len(state["players"]) < MIN_PLAYERS and state["lobby_job"] is not None:
            _cancel_job(state["lobby_job"])
            state["lobby_job"] = None
            await context.bot.send_message(
                chat_id, "⚠️ Dropped below minimum players — waiting for more players to join."
            )
        if not state["players"]:
            del tord_games[chat_id]
            await context.bot.send_message(chat_id, "🛑 Everyone left. Game cancelled.")
        return

    # started game
    if len(state["players"]) < MIN_PLAYERS:
        del tord_games[chat_id]
        await context.bot.send_message(
            chat_id, f"{reason}\n\n🛑 Not enough players left, game cancelled!", parse_mode="HTML"
        )
        return

    if idx < state["turn_index"] or (idx == state["turn_index"]):
        # keep turn_index pointing at the same "next" player after removal
        if state["turn_index"] >= len(state["players"]):
            state["turn_index"] = 0
    await context.bot.send_message(
        chat_id, f"{reason}\n\n<b>Updated turn order:</b>\n{_player_list_text(state)}", parse_mode="HTML"
    )

    if was_current_turn:
        await context.bot.send_message(
            chat_id,
            f"❕ {_mention(removed['id'], removed['name'])} left, skipping to next player.",
            parse_mode="HTML",
        )
        await _post_turn(chat_id, context)


# ---------------------------------------------------------------------------
# /cancel_tord
# ---------------------------------------------------------------------------
async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    state = tord_games.get(chat.id)

    if not state:
        await update.message.reply_text("There's no game to cancel")
        return

    if not await _can_manage(update, context, state):
        await update.message.reply_text("Only the game creator or a group admin in the game can do that.")
        return

    _cancel_job(state.get("lobby_job"))
    _cancel_job(state.get("cancel_job"))
    del tord_games[chat.id]
    await update.message.reply_html(
        f"🛑 The Truth or Dare game has been cancelled by "
        f"{_mention(update.effective_user.id, update.effective_user.first_name)}."
    )


# ---------------------------------------------------------------------------
# /close_tord
# ---------------------------------------------------------------------------
async def cmd_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    state = tord_games.get(chat.id)

    if not state:
        await update.message.reply_text("There's no game to close")
        return

    if not await _can_manage(update, context, state):
        await update.message.reply_text("Only the game creator or a group admin in the game can do that.")
        return

    if state["closed"]:
        await update.message.reply_text("This game is already closed!")
        return

    state["closed"] = True
    await update.message.reply_text("🔒 Game closed! No new players can join.")
