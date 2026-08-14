"""
Meme Hub Bot 😂
Publishes funny memes, jokes, GIFs, and humorous content on Telegram.

Commands:
  /start  - welcome message
  /meme   - fetch a trending meme GIF from Giphy
  /joke   - fetch a joke from icanhazdadjoke and render it as an image
  /random - randomly sends either a GIF meme or a joke image
  /help   - list commands
"""

import os
import random
import logging

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

from image_gen import render_joke_image

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")
API_NINJAS_KEY = os.getenv("API_NINJAS_KEY")

# Search terms rotated for variety when fetching "meme" GIFs
MEME_SEARCH_TERMS = [
    "funny meme", "reaction meme", "funny fail", "lol", "funny animal",
    "dank meme", "funny cat", "funny dog", "epic fail", "funny moment",
    "comedy", "hilarious", "funny reaction",
]

GIPHY_SEARCH_URL = "https://api.giphy.com/v1/gifs/search"
API_NINJAS_JOKES_URL = "https://api.api-ninjas.com/v1/jokes"


def fetch_giphy_gif() -> str | None:
    """Fetch a random trending/funny GIF URL from Giphy."""
    term = random.choice(MEME_SEARCH_TERMS)
    params = {
        "api_key": GIPHY_API_KEY,
        "q": term,
        "limit": 25,
        "rating": "pg-13",
    }
    try:
        resp = requests.get(GIPHY_SEARCH_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("data", [])
        if not results:
            return None
        choice = random.choice(results)
        return choice["images"]["original"]["url"]
    except Exception as e:
        logger.error(f"Giphy fetch failed: {e}")
        return None


def fetch_joke() -> dict | None:
    """Fetch a one-liner joke from API Ninjas."""
    headers = {"X-Api-Key": API_NINJAS_KEY}
    try:
        resp = requests.get(API_NINJAS_JOKES_URL, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data:
            return {"joke": data[0].get("joke")}
        return None
    except Exception as e:
        logger.error(f"Joke fetch failed: {e}")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "😂 Welcome to Meme Hub Bot!\n\n"
        "I post funny memes, jokes, and GIFs.\n\n"
        "Commands:\n"
        "/meme - get a funny GIF\n"
        "/joke - get a joke as an image\n"
        "/random - surprise me\n"
        "/help - show this again"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action("upload_video")
    gif_url = fetch_giphy_gif()
    if gif_url:
        await update.message.reply_animation(animation=gif_url)
    else:
        await update.message.reply_text("Couldn't fetch a meme GIF right now 😅 try again in a bit.")


async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action("upload_photo")
    joke_data = fetch_joke()
    if joke_data and joke_data.get("joke"):
        img_buf = render_joke_image(joke_data["joke"])
        await update.message.reply_photo(photo=img_buf)
    else:
        await update.message.reply_text("Couldn't fetch a joke right now 😅 try again in a bit.")


async def random_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if random.random() < 0.5:
        await meme(update, context)
    else:
        await joke(update, context)


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set in environment / .env")
    if not GIPHY_API_KEY:
        raise RuntimeError("GIPHY_API_KEY not set in environment / .env")
    if not API_NINJAS_KEY:
        raise RuntimeError("API_NINJAS_KEY not set in environment / .env")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("meme", meme))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("random", random_content))

    logger.info("Meme Hub Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
