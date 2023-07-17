import os
import telegram
from pytube import YouTube
from googletrans import Translator
from pysrt import SubRipFile, SubRipItem, SubRipTime

# Initialize the bot and the translator
bot = telegram.Bot(token='YOUR_TELEGRAM_BOT_TOKEN')
translator = Translator()

# Function to download captions, translate them and send them via telegram
def process_video(url, chat_id):
    yt = YouTube(url)
    captions = yt.captions.get_by_language_code('en')  # Assuming the video has English captions

    if captions is None:
        bot.send_message(chat_id=chat_id, text="No captions found for this video.")
        return

    # Download captions as srt
    srt_captions = captions.generate_srt_captions()
    with open('captions.srt', 'w') as f:
        f.write(srt_captions)

    # Load the srt file and translate each item
    subs = SubRipFile.open('captions.srt')
    for item in subs:
        translated_text = translator.translate(item.text, dest='fa').text
        item.text = translated_text

    # Save the translated srt file
    subs.save('translated_captions.srt', encoding='utf-8')

    # Send the file via telegram
    bot.send_document(chat_id=chat_id, document=open('translated_captions.srt', 'rb'))

    # Clean up
    os.remove('captions.srt')
    os.remove('translated_captions.srt')

# TODO: Set up your bot to call process_video with the appropriate arguments when it receives a message
