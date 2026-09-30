import os
import asyncio
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import yt_dlp

# Railway par secure rakhne ke liye environment variable se token uthayega
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

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

    status_msg = await update.message.reply_text("⏳ Processing audio...")
    
    output_template = "audio_%(id)s.%(ext)s"
    
    # YouTube bot-check error bypass karne ke liye updated player clients
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }, {
            'key': 'FFmpegMetadata',
        }],
        'outtmpl': output_template,
        'extractor_args': {'youtube': {'player_client': ['mweb', 'ios', 'android']}},
        'quiet': True,
        'no_warnings': True,
    }

    audio_file = None
    try:
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)

        await status_msg.edit_text("📥 Downloading from YouTube...")
        filename = await asyncio.to_thread(download)
        audio_file = filename.rsplit(".", 1)[0] + ".mp3"

        if not os.path.exists(audio_file):
            raise Exception("Audio conversion failed!")

        await status_msg.edit_text("📤 Uploading to Telegram...")
        
        with open(audio_file, 'rb') as audio:
            await update.message.reply_audio(
                audio=audio,
                title=os.path.basename(audio_file)
            )
        
        await status_msg.delete()

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
    
    print("ANJALI×MUSIC Bot is running successfully...")
    application.run_polling()

if __name__ == '__main__':
    main()
