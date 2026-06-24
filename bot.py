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
X_URL = "https://x.com
