import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import yt_dlp as ydl

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = '7517649657:AAEDy7hZCTst7Bv4elIEatr7AGc0Gg9TKhw'
BOT_NAME = 'Pikachu_MusicBot'
BOT_DESCRIPTION = 'I am a Pikachu_MusicBot. Use /search <song> to find and get audio files for your favorite songs.'

def search_song(query: str) -> str:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',  # Keep original extension
        'noplaylist': True,
        'default_search': 'ytsearch',  # Use ytsearch to perform a search
    }
    
    search_query = f"ytsearch:{query}"
    
    with ydl.YoutubeDL(ydl_opts) as ydl_obj:
        try:
            info = ydl_obj.extract_info(search_query, download=True)
            # Return the file path of the downloaded audio
            for entry in info['entries']:
                return f"song.{entry['ext']}"
        except Exception as e:
            logger.error(f"Error in search_song: {e}")
            return None

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text('Please provide a song name to search for.')
        return

    logger.info(f"Searching for song: {query}")
    audio_file_path = search_song(query)
    
    if audio_file_path and os.path.exists(audio_file_path):
        await update.message.reply_text('Found the song! Sending...')

        try:
            # Send the audio file
            with open(audio_file_path, 'rb') as audio_file:
                await update.message.reply_audio(audio=audio_file, filename=os.path.basename(audio_file_path))

        except Exception as e:
            await update.message.reply_text('Error sending the audio file.')
            logger.error(f"Error sending audio file: {e}")

        finally:
            # Clean up
            if os.path.exists(audio_file_path):
                os.remove(audio_file_path)
    else:
        await update.message.reply_text('Sorry, I could not find the song.')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (f"Hello! I'm {BOT_NAME}.\n\n"
                       f"{BOT_DESCRIPTION}\n\n"
                       f"Use /search <song> to find and get audio files.")
    await update.message.reply_text(welcome_message)

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler('search', search))
    application.add_handler(CommandHandler('start', start))
    
    # Start the bot
    logger.info(f"{BOT_NAME} is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
