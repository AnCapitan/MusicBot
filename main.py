import logging
import telebot
from moviepy.video.io.VideoFileClip import VideoFileClip
from pytube import YouTube, Search
from ShazamAPI import Shazam
import os

API_TOKEN = ''
logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(API_TOKEN, parse_mode=None)
URL_YOUTUBE = 'https://www.youtube.com/watch?v='
SAVE_DIR = 'data/shazam/'


def youtube_download(request_user, message):
    try:
        search = [request_user[i] for i in range(len(request_user))]
        create_request = str(Search(search).results[0]).replace('<pytube.__main__.YouTube object: videoId=', '').replace('>', '')
        request = YouTube(f'{URL_YOUTUBE}{create_request}')
        stream = request.streams.filter(only_audio=True).get_by_itag(140)
        file_music = str(stream.download(output_path=f'data/{message.chat.id}/'))
        bot.send_audio(message.chat.id, open(f'{file_music}', 'rb'))
        os.remove(file_music)
    except:
        bot.send_message(message.chat.id, f'Что то пошло не так, попробуйте снова', parse_mode='html')


@bot.message_handler(commands=['music'])
def search_music(message):
    bot.send_message(message.chat.id, f'Запрос обрабатывается', parse_mode='html')

    try:
        os.mkdir(f'data/{message.chat.id}')
    except:
        pass

    try:
        request_user = message.text.replace('/music', '').split()
        youtube_download(request_user, message)
    except:
        bot.send_message(message.chat.id, f'Что то пошло не так, попробуйте снова', parse_mode='html')


@bot.message_handler(content_types=['video', 'audio'])
def search_shazam(message):
    try:
        bot.send_message(message.chat.id, f'Запрос обрабатывается', parse_mode='html')
        file_name = f'{message.message_id}.mp4'
        file_id_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_id_info.file_path)
        with open(SAVE_DIR + "/" + file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
        video = VideoFileClip(os.path.join(f'{SAVE_DIR}/{file_name}'))
        video.audio.write_audiofile(os.path.join(f'{SAVE_DIR}/{file_name.replace("mp4", "mp3")}'))
        file_name_new = file_name.replace('mp4', 'mp3')
        mp4_file_content_to_recognize = open(f'{SAVE_DIR}{file_name_new}', 'rb').read()
        shazam = Shazam(
            mp4_file_content_to_recognize,
        )
        recognize_generator = shazam.recognizeSong()
        file_shazam = next(recognize_generator)
        result = f"{file_shazam[1]['track']['title']} {file_shazam[1]['track']['subtitle']}"
        os.remove(f'{SAVE_DIR}{file_name}')
        os.remove(f'{SAVE_DIR}{file_name_new}')
        bot.send_message(message.chat.id, result, parse_mode='html')
        result = result.split()
        youtube_download(result, message)
    except:
        bot.send_message(message.chat.id, f'Что то пошло не так, попробуйте снова', parse_mode='html')


if __name__ == '__main__':
    bot.infinity_polling()
