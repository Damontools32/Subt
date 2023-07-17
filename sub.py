import os
import telegram
from telegram.ext import Updater, MessageHandler, Filters
from youtube_transcript_api import YouTubeTranscriptApi
from pysrt import SubRipFile, SubRipItem, SubRipTime

# Initialize the bot
bot = telegram.Bot(token='YOUR_TELEGRAM_BOT_TOKEN')
updater = Updater(token='YOUR_TELEGRAM_BOT_TOKEN')
dispatcher = updater.dispatcher

# Function to download captions, translate them and send them via telegram
def process_video(url, chat_id):
    # Extract video_id from url
    video_id = url.split('=')[-1]

    # Get the auto-translated captions
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        auto_translated_transcript = transcript_list.find_generated_transcript(['fa'])
    except Exception as e:
        bot.send_message(chat_id=chat_id, text=f'Error getting auto-translated subtitles: {str(e)}')
        return

    # Convert the translated captions to SRT format
    subtitles = auto_translated_transcript.fetch()
    srt_subtitles = SubRipFile()
    for i, sub in enumerate(subtitles, 1):
        item = SubRipItem(
            index=i,
            start=SubRipTime.from_seconds(sub['start']),
            end=SubRipTime.from_seconds(sub['start'] + sub['duration']),
            text=sub['text']
        )
        srt_subtitles.append(item)

    # Write the SRT subtitles to a file
    filename = f"{video_id}.srt"
    srt_subtitles.save(filename, encoding='utf-8')

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
