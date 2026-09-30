import os
import asyncio
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from pytubefix import YouTube

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

    status_msg = await update.message.reply_text("⏳ Processing audio via pytubefix...")
    
    temp_file = None
    audio_file = None
    try:
        def download_audio():
            yt = YouTube(url)
            stream = yt.streams.get_audio_only()
            # Download file
            file_path = stream.download(filename="temp_audio.mp4")
            return file_path

        filename = await asyncio.to_thread(download_audio)
        temp_file = filename
        
        # FFmpeg ke zariye MP3 mein convert karna
        base, _ = os.path.splitext(filename)
        audio_file = base + ".mp3"
        
        cmd = f"ffmpeg -y -i \"{filename}\" -vn -ab 128k \"{audio_file}\""
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await proc.communicate()

        if not os.path.exists(audio_file):
            audio_file = filename # Agar conversion fail ho toh original file use karein

        await status_msg.edit_text("📤 Uploading to Telegram...")
        
        with open(audio_file, 'rb') as audio:
            await update.message.reply_audio(
                audio=audio,
                title="ANJALI×MUSIC Audio"
            )
        
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        if audio_file and os.path.exists(audio_file) and audio_file != temp_file:
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
    
    print("ANJALI×MUSIC Bot is running with pytubefix...")
    application.run_polling()

if __name__ == '__main__':
    main()
