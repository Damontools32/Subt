import os
import telegram
from telegram.ext import Updater, MessageHandler, Filters
from youtube_transcript_api import YouTubeTranscriptApi
from pysrt import SubRipFile, SubRipItem, SubRipTime
from googletrans import Translator

# Initialize the bot
bot = telegram.Bot(token='YOUR_TELEGRAM_BOT_TOKEN')
updater = Updater(token='YOUR_TELEGRAM_BOT_TOKEN')
dispatcher = updater.dispatcher

# Function to download captions, translate them and send them via telegram
def process_video(url, chat_id):
    # Extract video_id from url
    video_id = url.split('=')[-1]

    # Initialize the Translator
    translator = Translator()

    # Get the auto-generated English captions
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    except Exception as e:
        bot.send_message(chat_id=chat_id, text=f'Error getting English subtitles: {str(e)}')
        return

    # Convert the translated English captions to SRT format
    srt_subtitles = SubRipFile()
    for i, sub in enumerate(transcript_list, 1):
        # Translate English text to Persian
        translated_text = translator.translate(sub['text'], dest='fa').text

        # Create a SubRipItem with the translated text
        item = SubRipItem(
            index=i,
            start=SubRipTime.from_seconds(sub['start']),
            end=SubRipTime.from_seconds(sub['start'] + sub['duration']),
            text=translated_text
        )
        srt_subtitles.append(item)

    # Write the SRT subtitles to a file
    filename = f"{video_id}.srt"
    srt_subtitles.save(filename, encoding='utf-8')

    # Send the file via telegram
    with open(filename, 'rb') as f:
        bot.send_document(chat_id=chat_id, document=f)

    # remove the file after sending
    os.remove(filename)

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
