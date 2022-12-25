import logging
from pytube import YouTube, Search
from ShazamAPI import Shazam
import telebot
import os

API_TOKEN = ''
logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(API_TOKEN, parse_mode=None)
PWD = ''
URL_YOUTUBE = 'https://www.youtube.com/watch?v='


def youtube_download(request_user, message):
    try:
        search = [request_user[i] for i in range(len(request_user))]
        check = str(Search(search).results[0]).replace('<pytube.__main__.YouTube object: videoId=', '').replace('>', '')
        yt = YouTube(f'{URL_YOUTUBE}{check}')
        stream = yt.streams.filter(only_audio=True).get_by_itag(140)
        input_file = str(stream.download(output_path=f'data/{message.chat.id}/')).replace(PWD, '')
        bot.send_audio(message.chat.id, open(f'{input_file}', 'rb'))
        os.remove(input_file)
    except:
        bot.send_message(message.chat.id, f'Что то пошло не так, попробуйте снова yo', parse_mode='html')


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
        bot.send_message(message.chat.id, f'Что то пошло не так, попробуйте снова se', parse_mode='html')


@bot.message_handler(content_types=['video', 'audio'])
def search_shazam(message):
    try:
        bot.send_message(message.chat.id, f'Запрос обрабатывается', parse_mode='html')
        file_name = message.video.file_name
        file_id_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_id_info.file_path)
        save_dir = 'data/shazam'
        with open(save_dir + "/" + file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
        mp4_file_content_to_recognize = open(f'data/shazam/{file_name}', 'rb').read()
        shazam = Shazam(
            mp4_file_content_to_recognize,
        )
        recognize_generator = shazam.recognizeSong()
        check = next(recognize_generator)
        result = f"{check[1]['track']['title']} {check[1]['track']['subtitle']}"
        os.remove(f'data/shazam/{file_name}')
        bot.send_message(message.chat.id, result, parse_mode='html')
        result = result.split()
        youtube_download(result, message)
    except:
        bot.send_message(message.chat.id, f'Что то пошло не так, попробуйте снова se', parse_mode='html')


if __name__ == '__main__':
    try:
        os.mkdir(f'data/shazam')
    except:
        pass
    bot.infinity_polling()

