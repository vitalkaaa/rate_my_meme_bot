import os

from telebot import apihelper

from meme_bot import MemeBot
from models import init_models


apihelper.proxy = {'https': 'https://sxPjdB:Q3D0FC@196.16.112.200:8000'}

BOT_TOKEN = os.getenv("BOT_TOKEN", '936423319:AAHIzkoM_Sos-epjSngJDGv_YJTAS6Bv9oo')
bot = MemeBot(BOT_TOKEN)


@bot.message_handler(content_types=['text', 'video', 'photo', 'document'])
def message_handler(message):
    bot.meme_handler(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    bot.vote_handler(call)


if __name__ == '__main__':
    print('Start', flush=True)
    init_models()
    bot.run_pooling()
    bot.run_scheduler()


