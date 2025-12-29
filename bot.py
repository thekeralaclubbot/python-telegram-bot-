import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Updated with your Bot Token
TOKEN = '8398909125:AAH91JI9ruXiIaPhn7A0lcQLFPmC5szc140'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I am a Video/Audio Downloader Bot.\n\n"
        "Send me any social media video link to start."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "http" not in url:
        await update.message.reply_text("Please send a valid link 🔗")
        return

    keyboard = [
        [InlineKeyboardButton("🎥 Video", callback_data=f"vid|{url}")],
        [InlineKeyboardButton("🎵 Audio (MP3)", callback_data=f"aud|{url}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("What would you like to download?", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    choice, url = query.data.split('|')
    chat_id = query.message.chat_id
    sent_msg = await context.bot.send_message(chat_id=chat_id, text="Downloading... Please wait ⏳")

    if choice == "vid":
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }
    else:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if choice == "aud":
                filename = os.path.splitext(filename)[0] + ".mp3"

        await sent_msg.edit_text("Uploading file... 📤")
        
        if choice == "vid":
            await context.bot.send_video(chat_id=chat_id, video=open(filename, 'rb'))
        else:
            await context.bot.send_audio(chat_id=chat_id, audio=open(filename, 'rb'))
        
        if os.path.exists(filename):
            os.remove(filename)
        await sent_msg.delete()

    except Exception as e:
        await sent_msg.edit_text(f"Sorry, an error occurred: {str(e)}")

def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
