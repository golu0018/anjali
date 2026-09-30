import os
import random
import asyncio
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Aapki di gayi proxy list
PROXY_LIST = [
    "px023005.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px022505.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px022507.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px051003.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px043005.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px043006.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px043004.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px410701.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px015601.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px032004.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px014004.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px490701.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px032002.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px591801.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px022409.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px022408.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px173003.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px420602.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px031901.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px490402.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px460101.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px490401.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px041201.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px041202.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px470108.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px051703.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px040706.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px460403.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px870303.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px400501.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px380101.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px013301.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px013302.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px019603.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px520401.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px014236.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px040805.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px121102.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px013304.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px440401.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px016104.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px180801.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px121001.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px013403.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px013401.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px150902.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px270401.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px591203.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px591201.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px152201.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px241104.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px241102.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px331101.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px400408.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px1260303.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "px023005.pointtoserver.com:10780:purevpn0s7525859:zs1sexmo902s",
    "px022505.pointtoserver.com:10780:purevpn0s7525859:zs1sexmo902s",
    "px022507.pointtoserver.com:10780:purevpn0s7525859:zs1sexmo902s",
    "px051003.pointtoserver.com:10780:purevpn0s7525859:zs1sexmo902s",
]

def get_random_proxy():
    raw_proxy = random.choice(PROXY_LIST)
    parts = raw_proxy.split(":")
    if len(parts) == 4:
        host, port, user, pwd = parts
        return f"http://{user}:{pwd}@{host}:{port}"
    return None

async def post_init(application):
    commands = [
        BotCommand("start", "Bot ko start karein")
    ]
    await application.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🦋 **Welcome to ANJALI×MUSIC World!** 🦋\n\n"
        "Yahan aap kisi bhi YouTube video ka link bhej kar "
        "turant fast high-quality audio download kar sakte hain.\n\n"
        "✨ **Proxy-Protected Mode Enabled!** ✨"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    url = update.message.text.strip()
    if not ("youtube.com" in url or "youtu.be" in url):
        return

    status_msg = await update.message.reply_text("⏳ Downloading via secure Proxy...")

    proxy_url = get_random_proxy()
    audio_file = None

    try:
        def download_with_proxy():
            nonlocal audio_file
            ydl_opts = {
                'format': 'bestaudio/best',
                'proxy': proxy_url,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }],
                'outtmpl': '%(id)s.%(ext)s',
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                audio_file = ydl.prepare_filename(info)
                # Extension ko mp3 mein badlein kyunki FFmpeg extract karega
                base, _ = os.path.splitext(audio_file)
                audio_file = base + ".mp3"

        await asyncio.to_thread(download_with_proxy)

        if audio_file and os.path.exists(audio_file):
            await status_msg.edit_text("📤 Uploading to Telegram...")
            with open(audio_file, 'rb') as audio:
                await update.message.reply_audio(
                    audio=audio,
                    title="ANJALI×MUSIC Audio"
                )
            await status_msg.delete()
        else:
            raise Exception("Audio file download nahi ho payi.")

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
    
    print("ANJALI×MUSIC Bot is running with Proxy Rotation...")
    application.run_polling()

if __name__ == '__main__':
    main()
