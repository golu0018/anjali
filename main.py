import os
import asyncio
import httpx
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
COBALT_API_URL = "https://api.cobalt.tools/api/json"

async def post_init(application):
    commands = [
        BotCommand("start", "Bot ko start karein aur welcome message dekhein")
    ]
    await application.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🦋 **Welcome to ANJALI×MUSIC World!** 🦋\n\n"
        "Yahan aap kisi bhi YouTube video ka link bhej kar "
        "turant fast high-quality audio download kar sakte hain.\n\n"
        "✨ **Kaise use karein?**\n"
        "Bas koi bhi YouTube ka link yahan paste karke bhej dein!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    url = update.message.text.strip()
    
    if not ("youtube.com" in url or "youtu.be" in url):
        return

    status_msg = await update.message.reply_text("⏳ Processing audio via Cobalt...")
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "audioFormat": "mp3",
        "downloadMode": "audio"
    }

    audio_file = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(COBALT_API_URL, json=payload, headers=headers)
            data = response.json()

        if data.get("status") in ["redirect", "stream", "picker"]:
            audio_url = data.get("url")
            if not audio_url and "picker" in data:
                audio_url = data["picker"][0]["url"]

            await status_msg.edit_text("📥 Downloading & Uploading to Telegram...")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                audio_res = await client.get(audio_url)
                audio_bytes = audio_res.content

            audio_file = "downloaded_audio.mp3"
            with open(audio_file, "wb") as f:
                f.write(audio_bytes)

            with open(audio_file, "rb") as audio:
                await update.message.reply_audio(
                    audio=audio,
                    title="ANJALI×MUSIC Audio"
                )
            
            await status_msg.delete()
        else:
            err_msg = data.get("text", "Download failed from Cobalt API")
            await status_msg.edit_text(f"❌ Error: {err_msg}")

    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        if audio_file and os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except:
                pass

def main():
    custom_request = HTTPXRequest(
        connection_pool_size=8,
        read_timeout=30.0,
        write_timeout=30.0,
        connect_timeout=30.0,
    )

    application = ApplicationBuilder().token(BOT_TOKEN).request(custom_request).post_init(post_init).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("ANJALI×MUSIC Bot is running with Cobalt API...")
    application.run_polling()

if __name__ == '__main__':
    main()
