import os
import asyncio
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Aapke cookies ko automatic Netscape format mein convert karke cookies.txt banane ka function
RAW_COOKIES = "LOGIN_INFO=AFmmF2swRQIgKCynSiXJO8z4P6VevpWHNVAT8bNrbqm9S2lzLKzzISYCIQCvKXFeuiJw_oH8U_-5gfS05ZY5rtRwHmt4R379_MmKcA:QUQ3MjNmenllQ2swR2RzaTZERkMxbVlfanZucnI4YURmVEhDUllvcFNrUmt0dzNyQlctQXpCVXBRU0l4cU1KR1hEWWZKSnltSzNpN0V5SXhZakxKS0tJdVRfX0U0X184bDNZYUhrSGVoclNoNEljUDhrNE1CTDlRNVNnVW5vSU9uZ1FldUtOeU1XRWpLSThsOGFlUzVXVk1VNzdMLWlhb1N3; YSC=tvU-szEtMXc; VISITOR_INFO1_LIVE=WPpU4ryUpeY; VISITOR_PRIVACY_METADATA=CgJJThIEGgAgGQ%3D%3D; PREF=f6=40000000&f7=100&tz=Asia.Calcutta; __Secure-1PSIDTS=sidts-CjUBPWEu2Z2wjfAk9sWex0Wci2y1Xb8XgVoCYrb_XWekBlIvZNR-FkQp0W-mjDpHHYDucZTl2hAA; HSID=APGsP5Lqo0pIXd-O2; SSID=Aw5N1K_iGuOEJ_XPK; APISID=BIK6BTSNTYrOxNZI/Ax_8Lj4c0vLHYsVnR; SAPISID=SJL-O-X3TQ3e9E2-/AolnuYHlKCuhSzu1h; __Secure-1PAPISID=SJL-O-X3TQ3e9E2-/AolnuYHlKCuhSzu1h; __Secure-3PAPISID=SJL-O-X3TQ3e9E2-/AolnuYHlKCuhSzu1h; __Secure-YNID=21.YT=Snftf10dLX0nCVm5bVOCHCm72QVhpsgeuJziwkJa11fJwV39BwFRxvREvCqLUH04FGl3N2zuCy9oZHBju49IkR2NvBar9b-5roKXBNTCzkZ6476KsNy9n_4atgp-A4LZXWKPs3qy74WGWDzivIRESSwLET_ilV4ML1whEhHJ1iJMBCCvBWTmePWEDYfBB0RXSy7VF2fe3k1K5buscKXBMLUrn278GS1h8jv2kX5_8hXGHKmdf8yon94Ea_ujawsRf-_8TId3IHH96VOmqY_B74dMh3ElYALtIPtNa3_kVdK2VzIIJFl9_THOwy5M8qvTKgaeUR0CrzsCh89GNWEGTQ; SID=g.a000BgnIoEd8YdPAzjPuOd2BNszAkr5XZjSBUICT-PVFsi0x9z3IMx7rB9K0vT7sNfoiV4q-DgACgYKAWsSARUSFQHGX2MiQ-oKj6L9DoWD1UcbDUnSWBoVAUF8yKqI1HP5yZA2KgjZ9e9cu9c60076; __Secure-1PSID=g.a000BgnIoEd8YdPAzjPuOd2BNszAkr5XZjSBUICT-PVFsi0x9z3IFDYP2FZny8PxC3RgIkkgMgACgYKAcgSARUSFQHGX2MiP4kTxZbcRETLbl9M0hkF7hoVAUF8yKpTdaRlD_sbP_JiDFnQoHNl0076; __Secure-3PSIDTS=sidts-CjUBPWEu2Z2wjfAk9sWex0Wci2y1Xb8XgVoCYrb_XWekBlIvZNR-FkQp0W-mjDpHHYDucZTl2hAA; __Secure-3PSID=g.a000BgnIoEd8YdPAzjPuOd2BNszAkr5XZjSBUICT-PVFsi0x9z3IFLuWYxbD8zuhd8ZqLTpuqAACgYKAUgSARUSFQHGX2MiSG0i_a_LPVOC1oBVshrk9xoVAUF8yKp2N7-BmaAqg7QK5k_UkbHt0076; __Secure-ROLLOUT_TOKEN=CJyYic2bnp-cYBCi-sfZk9ySAxiwq6WJzZWXAw%3D%3D; SIDCC=AKEyXzV5kSSe4Px_TbpS04edt4otMn_2oS7Qg3aUojD4xKGw1TiLK56tytHu5sKRqNIKTzxoYg; __Secure-1PSIDCC=AKEyXzUoZj0vPa6_4EllV67LGCgYzHhnzjz9TSaSZmdEMwP8j9N8BHp2zDxey9HrLmRJAG9p4w; __Secure-3PSIDCC=AKEyXzW1b3gcXNFVHMyrBKbrShqInoQgV8NrB8jRNkFVYZN-mdj_BZKgdUvwMAhqgof781vRnA"

def setup_cookies():
    try:
        cookie_lines = ["# Netscape HTTP Cookie File\n"]
        for item in RAW_COOKIES.split(";"):
            if "=" in item:
                parts = item.strip().split("=", 1)
                if len(parts) == 2:
                    name, val = parts
                    cookie_lines.append(f".youtube.com\tTRUE\t/\tTRUE\t0\t{name}\t{val}\n")
        with open("cookies.txt", "w") as f:
            f.writelines(cookie_lines)
    except Exception as e:
        print(f"Cookie setup error: {e}")

setup_cookies()

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
        'cookiefile': 'cookies.txt',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
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
    
    print("ANJALI×MUSIC Bot is running successfully with Cookies...")
    application.run_polling()

if __name__ == '__main__':
    main()
