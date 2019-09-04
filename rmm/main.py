import os

import telebot
from telebot import apihelper

from engine import BotEngine
from models import init_models
from utils import vote_keyboard

apihelper.proxy = {'https': 'https://sxPjdB:Q3D0FC@196.16.112.200:8000'}

BOT_TOKEN = os.getenv("BOT_TOKEN", '936423319:AAHIzkoM_Sos-epjSngJDGv_YJTAS6Bv9oo')
bot = telebot.TeleBot(BOT_TOKEN)
engine = BotEngine()


@bot.message_handler(content_types=['text', 'video', 'photo', 'document'])
def message_handler(message):
    user_id = str(message.from_user.id)
    engine.save_user(message)
    message_info = engine.get_message_info(message)

    bot.send_message(user_id, message_info['back_text'], reply_to_message_id=message_info['msg_id'])

    # send if it is meme
    if message_info['allowed_file']:
        engine.cache_last_meme_date(user_id)
        file_info = bot.get_file(message_info['file_id'])
        binary_file = bot.download_file(file_info.file_path)

        msg_resp = None
        if message_info['file_type'] in ('video', 'animation'):
            msg_resp = bot.send_video('@rate_my_meme', binary_file, reply_markup=vote_keyboard())
        if message_info['file_type'] == 'photo':
            msg_resp = bot.send_photo('@rate_my_meme', binary_file, reply_markup=vote_keyboard())

        if msg_resp:
            engine.save_meme(user_id, message_info['file_type'], message_info['file_id'], msg_resp.message_id)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.from_user.id)
    engine.save_user(call)
    callback_info = engine.get_callback_info(call)

    if callback_info['type'] == 'vote':
        bot.answer_callback_query(call.id, text=callback_info['back_text'])

if __name__ == '__main__':
    print('Start', flush=True)
    init_models()
    bot.polling(none_stop=True, interval=1)
    engine.run_scheduler()


