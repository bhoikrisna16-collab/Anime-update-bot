
import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
logging.basicConfig(
format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
ANILIST_URL = "https://graphql.anilist.co"
QUERY = """
query ($search: String) {
Media (search: $search, type: ANIME) {
title {
romaji
english
}
status
episodes
nextAiringEpisode {
episode
timeUntilAiring
}
siteUrl
}
}
"""
def fetch_anime_info(anime_name: str) -> str:
 try:    
    response = requests.post(
    ANILIST_URL,
    json={"query": QUERY, "variables": {"search": anime_name}},
    timeout=10,
    )
    data = response.json()
    media = data.get("data", {}).get("Media")
    if not media:
        return f"No anime found for '{anime_name}'."
    title = media["title"]["english"] or media["title"]["romaji"]
    status = media["status"]
    total_eps = media["episodes"] or "Unknown"
    next_ep = media["nextAiringEpisode"]
    url = media["siteUrl"]
    msg = f"{title}\nStatus: {status}\nTotal Episodes: {total_eps}\n"
    if next_ep:
        ep_num = next_ep["episode"]
        seconds = next_ep["timeUntilAiring"]
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, _ = divmod(rem, 60)
        msg += f"Next Episode ({ep_num}): in {days}d {hours}h {minutes}m\n"
        msg += f"More Info"
        return msg
 except Exception as e:
        logging.error(f"Error fetching anime data: {e}")
        return "Failed to fetch anime updates. Please try again later."
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await update.message.reply_text(
        "Send me any anime name to get its airing status and next episode update!"
        )
        async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            anime_name = update.message.text.strip()
        if not anime_name:
            return
        reply = fetch_anime_info(anime_name)
                await update.message.reply_text(reply, parse_mode="Markdown", disable_web_page_preview=True)
        def main() -> None:
            application = Application.builder().token(TOKEN).build()
            application.add_handler(CommandHandler("start", start))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            application.run_polling()
            if name == "main":
                main()

