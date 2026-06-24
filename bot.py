import os
import re
import json
import logging
import httpx
from datetime import time
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats,
    BotCommandScopeChat,
)
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
COMMUNITY_GROUP_CHAT_ID = -1004367924897
FAQ_GROUP_CHAT_ID = -1004341481702
ANNOUNCEMENTS_CHAT_ID = -1004447682804

CONTRACT_ADDRESS = ""

COMMUNITY_CHAT_URL = "https://t.me/+yxoJp8zrYeU0Mjlk"
ANNOUNCEMENTS_URL = "https://t.me/RegulardudeRG"
X_URL = "https://x.com/regulardudecoin?s=11"
FAQ_URL = "https://t.me/+VN5-dg0cZZk2Mzc0"

WELCOME_TEXT = (
    "Welcome to $RGDUDE 🚀\n\n"
    "Official portal for everything below 👇"
)

POLL_STATE_FILE = "poll_state.json"
POLL_TIMEZONE = ZoneInfo("Europe/Amsterdam")
POLL_HOUR = 17
POLL_MINUTE = 0

POLLS = [
    {"question": "Are you a regular dude?", "options": ["Yes 👍", "Trying", "Kinda", "No idea", "No"]},
    {"question": "How was your day today?", "options": ["Chill 👍", "Good", "Stressful", "Bad", "Confused"]},
    {"question": "What are you doing right now?", "options": ["Working", "School", "Chilling 👍", "Sleeping", "Scrolling"]},
    {"question": "What did you eat today?", "options": ["Same meal 👍", "Something new", "Skipped", "Not sure"]},
    {"question": "Your current mood is:", "options": ["Good 👍", "Okay", "Bad", "Tired", "Lost"]},
    {"question": "After work/school you usually:", "options": ["Netflix 👍", "Gaming", "Scroll phone", "Sleep", "Work more"]},
    {"question": "How productive are you today?", "options": ["Very 👍", "Normal", "Lazy", "Not at all", "No idea"]},
    {"question": "Be honest, you are:", "options": ["A regular dude 👍", "Hustler", "Degen", "Confused", "Trying"]},
    {"question": "How often do you do nothing?", "options": ["Daily 👍", "Often", "Sometimes", "Rarely", "Never"]},
    {"question": "Are you into crypto?", "options": ["Yes 👍", "Learning", "No", "Just memes", "Confused"]},
    {"question": "Your energy today:", "options": ["High 🚀", "Normal 👍", "Low", "Dead", "Sleeping"]},
    {"question": "What are you right now?", "options": ["Productive", "Lazy", "Tired", "Chilling 👍", "Lost"]},
    {"question": "How do you feel about life?", "options": ["Good 👍", "Okay", "Bad", "Confused", "No clue"]},
    {"question": "What describes you best?", "options": ["Regular dude 👍", "Hustler", "Gamer", "Student", "Worker"]},
    {"question": "What are you doing most today?", "options": ["Work", "School", "Gaming", "Scrolling 👍", "Sleeping"]},
    {"question": "Are you ready for something big?", "options": ["Yes 👍", "Maybe", "No", "Not sure", "Watching"]},
    {"question": "How active are you here?", "options": ["Very 👍", "Sometimes", "Rarely", "First time", "Silent"]},
    {"question": "What do you do in free time?", "options": ["Netflix 👍", "Gaming", "Sleep", "Scroll", "Nothing"]},
    {"question": "Your vibe today:", "options": ["Chill 👍", "Stressed", "Tired", "Focused", "Lost"]},
    {"question": "How 'regular' are you today?", "options": ["Very 👍", "Normal", "Not really", "Degen mode", "Confused"]},
    {"question": "What's your current status?", "options": ["Working", "Chilling 👍", "Sleeping", "Busy", "Lost"]},
    {"question": "Do you feel motivated?", "options": ["Yes 👍", "Kinda", "No", "Never", "Not sure"]},
    {"question": "How often do you check Telegram?", "options": ["Always 👍", "Often", "Sometimes", "Rarely", "First time"]},
    {"question": "What are you waiting for?", "options": ["Payday 👍", "Weekend", "Nothing", "Crypto pump", "No idea"]},
    {"question": "Are you consistent in life?", "options": ["Yes 👍", "Trying", "No", "Not really", "Confused"]},
    {"question": "How do you spend evenings?", "options": ["Netflix 👍", "Gaming", "Working", "Scrolling", "Sleeping"]},
    {"question": "What's your mindset today?", "options": ["Positive 👍", "Neutral", "Negative", "Tired", "Lost"]},
    {"question": "Are you focused today?", "options": ["Yes 👍", "Kinda", "No", "Distracted", "Not sure"]},
    {"question": "What best describes you?", "options": ["Regular dude 👍", "Degen", "Hustler", "Student", "Worker"]},
    {"question": "Final question: are you still here?", "options": ["Yes 👍", "Obviously", "Maybe", "No", "Just watching"]},
]


def _load_poll_state() -> dict:
    if os.path.exists(POLL_STATE_FILE):
        try:
            with open(POLL_STATE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not read poll state, resetting: {e}")
    return {"index": 0}


def _save_poll_state(state: dict) -> None:
    try:
        with open(POLL_STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        logger.warning(f"Could not save poll state: {e}")


async def send_daily_poll(context: ContextTypes.DEFAULT_TYPE) -> None:
    state = _load_poll_state()
    idx = state["index"] % len(POLLS)
    poll = POLLS[idx]
    try:
        await context.bot.send_poll(
            chat_id=ANNOUNCEMENTS_CHAT_ID,
            question=poll["question"],
            options=poll["options"],
            is_anonymous=True,
            allows_multiple_answers=False,
        )
        state["index"] = (idx + 1) % len(POLLS)
        _save_poll_state(state)
    except Exception as e:
        logger.warning(f"Could not send daily poll: {e}")


async def send_portal_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("📢 Announcements", url=ANNOUNCEMENTS_URL)],
        [InlineKeyboardButton("💬 Community Chat", url=COMMUNITY_CHAT_URL)],
        [InlineKeyboardButton("🐦 X (Twitter)", url=X_URL)],
        [InlineKeyboardButton("❓ FAQ", url=FAQ_URL)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_TEXT, reply_markup=reply_markup)


async def x_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("🐦 X (Twitter)", url=X_URL)]]
    await update.message.reply_text("Follow us on X:", reply_markup=InlineKeyboardMarkup(keyboard))


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user = update.effective_user
    if chat.type != "private":
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ("administrator", "creator"):
            return
    await update.message.reply_text(f"Chat ID: `{chat.id}`", parse_mode="Markdown")


async def handle_left_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.delete()
    except Exception as e:
        logger.warning(f"Could not delete left-member message: {e}")


async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    try:
        await update.message.delete()
    except Exception as e:
        logger.warning(f"Could not delete join message: {e}")
    if chat.id == COMMUNITY_GROUP_CHAT_ID:
        for member in update.message.new_chat_members:
            if member.is_bot:
                continue
            if member.username:
                mention = f"@{member.username}"
            else:
                mention = f'<a href="tg://user?id={member.id}">{member.first_name}</a>'
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"👋Welcome {mention}!",
                parse_mode="HTML",
            )


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not CONTRACT_ADDRESS:
        await update.message.reply_text("🚀 Token not live yet")
        return
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{CONTRACT_ADDRESS}"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            data = resp.json()
        pairs = data.get("pairs")
        if not pairs:
            await update.message.reply_text("🚀 Token not live yet")
            return
        pair = pairs[0]
        price_usd = float(pair.get("priceUsd", 0))
        market_cap = pair.get("fdv") or pair.get("marketCap") or 0
        change_24h = pair.get("priceChange", {}).get("h24", "?")
        pair_url = pair.get("url", "")
        text = (
            f"$RGDUDE 🚀\n\n"
            f"💰 Price: ${price_usd:.8f}\n"
            f"📊 Market Cap: ${market_cap:,.0f}\n"
            f"📈 24h: {change_24h}%\n"
            f"🔗 {pair_url}"
        )
        await update.message.reply_text(text)
    except Exception as e:
        logger.warning(f"Price fetch failed: {e}")
        await update.message.reply_text("Kon de prijs niet ophalen, probeer het zo nog eens.")


async def post_init(application: Application) -> None:
    try:
        await application.bot.set_my_commands(
            [
                BotCommand("start", "Open het $RGDUDE portal"),
                BotCommand("price", "Bekijk de actuele $RGDUDE prijs"),
            ],
            scope=BotCommandScopeAllPrivateChats(),
        )
    except Exception as e:
        logger.warning(f"Could not set private commands: {e}")
    try:
        await application.bot.set_my_commands(
            [BotCommand("portal", "Open het $RGDUDE portal")],
            scope=BotCommandScopeAllGroupChats(),
        )
    except Exception as e:
        logger.warning(f"Could not set group commands: {e}")
    try:
        await application.bot.set_my_commands(
            [
                BotCommand("portal", "Open het $RGDUDE portal"),
                BotCommand("price", "Bekijk de actuele $RGDUDE prijs"),
            ],
            scope=BotCommandScopeChat(chat_id=COMMUNITY_GROUP_CHAT_ID),
        )
    except Exception as e:
        logger.warning(f"Could not set community-specific commands: {e}")


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is not set.")

    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    x_trigger_chat_ids = [COMMUNITY_GROUP_CHAT_ID]
    if FAQ_GROUP_CHAT_ID:
        x_trigger_chat_ids.append(FAQ_GROUP_CHAT_ID)

    application.add_handler(CommandHandler("start", send_portal_menu, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("price", price, filters=filters.ChatType.PRIVATE | filters.Chat(chat_id=COMMUNITY_GROUP_CHAT_ID)))
    application.add_handler(CommandHandler("portal", send_portal_menu, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("chatid", chatid))
    application.add_handler(MessageHandler(
        filters.Regex(re.compile(r"^x$", re.IGNORECASE)) & filters.Chat(chat_id=x_trigger_chat_ids),
        x_link
    ))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_member))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, handle_left_member))

    application.job_queue.run_daily(
        send_daily_poll,
        time=time(hour=POLL_HOUR, minute=POLL_MINUTE, tzinfo=POLL_TIMEZONE),
        name="rgdude_daily_poll",
    )

    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
