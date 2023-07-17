import os
import telegram
from telegram.ext import Updater, MessageHandler, Filters
from pytube import YouTube
from googletrans import Translator
from pysrt import SubRipFile

# Initialize the bot and the translator
bot = telegram.Bot(token='YOUR_TELEGRAM_BOT_TOKEN')
updater = Updater(token='YOUR_TELEGRAM_BOT_TOKEN')
dispatcher = updater.dispatcher
translator = Translator()

# Function to download captions, translate them and send them via telegram
def process_video(url, chat_id):
    # Download the video
    yt = YouTube(url)

    # Download the captions
    caption = yt.captions.get_by_language_code('en')
    srt_captions = caption.generate_srt_captions()

    # Translate the captions
    translated_captions = ""
    for line in srt_captions.splitlines():
        translation = translator.translate(line, dest='fa')
        translated_captions += translation.text + "\n"

    # Write the translated captions to a file
    filename = "translated_captions.srt"
    with open(filename, 'w') as f:
        f.write(translated_captions)

    # Send the file via telegram
    bot.send_document(chat_id=chat_id, document=open(filename, 'rb'))

# Define a function to handle incoming messages
def handle_message(update, context):
    # Call process_video with the text of the message as the URL and the chat_id
    process_video(update.message.text, update.message.chat_id)

# Add the message handler to the dispatcher
message_handler = MessageHandler(Filters.text, handle_message)
dispatcher.add_handler(message_handler)

# Start the bot
updater.start_polling()
updater.idle()
