# 😂 Meme Hub Bot

A Telegram bot that publishes funny memes, jokes, and GIFs.

- `/meme` — fetches a random funny/trending GIF from **Giphy**
- `/joke` — fetches a joke from **API Ninjas** and renders it as an image (generated gradient background + bold meme-style text, via Pillow — no paid image API needed)
- `/random` — sends either a meme GIF or a joke image at random
- `/start`, `/help` — shows the command list

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   Copy `.env.example` to `.env` and fill in:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   GIPHY_API_KEY=your_giphy_api_key_here
   API_NINJAS_KEY=your_api_ninjas_key_here
   ```
   - Get your Telegram bot token from [@BotFather](https://t.me/BotFather).
   - Get your Giphy API key from [developers.giphy.com](https://developers.giphy.com/).
   - Get your API Ninjas key from your [API Ninjas profile page](https://api-ninjas.com/profile) (free tier: 3,000 calls/month across all their APIs, renews monthly).

3. **Run locally**
   ```bash
   python bot.py
   ```

## Deploying (Railway)

1. Push this folder to a GitHub repo.
2. Create a new Railway project from that repo.
3. In Railway's project settings, add the environment variables `TELEGRAM_BOT_TOKEN` and `GIPHY_API_KEY`.
4. Railway will detect the `Procfile` and run the bot as a worker process automatically.

## Notes

- Giphy's free tier has a rate limit (roughly 100 requests/hour on the beta key, 42 requests/hour on production keys with 1,000/day) — plenty for personal/small group bot use. If Giphy applies stricter limits than expected, consider caching a few results.
- Backgrounds for joke images are generated with color gradients (no external image API), so `/joke` always works even if an image API were ever unavailable.
- If Giphy's API ever becomes unstable or restricted (like Tenor's), an easy swap-in alternative is **Klipy**, another free GIF API — only `fetch_giphy_gif()` in `bot.py` would need to change.
