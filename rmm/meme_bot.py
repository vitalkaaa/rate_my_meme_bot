import time
from threading import Thread

import schedule
import telebot

from models import Meme, User
from utils import vote_keyboard


class MemeBot(telebot.TeleBot):
    def __init__(self, token):
        super(MemeBot, self).__init__(token=token)

    def command_handler(self, message):
        user_id = str(message.chat.id)

        if message.text.split(' ')[0].startswith('/start'):
            if not User.is_exists(user_id):
                username = '@' + message.from_user.username
                fullname = str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)
                fullname = fullname.replace('None', '') if fullname.replace('None', '') != '' else None
                user = User(user_id, username, fullname).save()
                self.send_message(user_id, 'Спасибо за регистрацию!')
                print(f'{user} have registred')

    def meme_handler(self, message: telebot.types.Message):
        user_id = message.from_user.id
        file_id = None
        file_type = None

        user = User.get(user_id)

        if message.text and message.text.startswith('/'):
            self.command_handler(message)

        if message.json.get('photo'):
            file_type = 'photo'
            file_id = message.json['photo'][-1]['file_id']

        if message.json.get('video'):
            file_type = 'video'
            file_id = message.json['video']['file_id']

        if message.json.get('animation'):
            file_type = 'animation'
            file_id = message.json['animation']['file_id']

        if file_id and file_type in ('video', 'animation', 'photo'):
            allowed_file = False

            if file_type in ('video', 'animation'):
                allowed_file = True
                back_text = 'Сейчас опубликуем ваш мем'
            elif file_type == 'photo':
                allowed_file = True
                back_text = 'Сейчас опубликуем ваш мем'
            else:
                back_text = 'Можно отправить видео, картинку или анимацию, ' \
                            'а так же репостить их из других из других каналов'

            self.send_message(user_id, back_text)
            meme = Meme(user_id, file_type, file_id).save()

            if allowed_file:
                file_info = self.get_file(file_id)
                binary_file = self.download_file(file_info.file_path)
                self.send_video('@rate_my_meme', binary_file, reply_markup=vote_keyboard())

            print(f'{user} have posted {meme}')

    def vote_handler(self, call: telebot.types.CallbackQuery):
        user_id = call.from_user.id
        msg_id = call.message.message_id
        mark = int(call.data)

        user = User.get(user_id)
        print(user)

    def run_scheduler(self):
        def scheduler_worker():
            # schedule.every(4).seconds.do(self.send_daily_results)
            # print('sending daily rating', flush=True)
            # schedule.every().day.at("00:00").do(self.send_daily_results)

            while True:
                schedule.run_pending()
                time.sleep(1)

        thread = Thread(target=scheduler_worker, args=())
        thread.daemon = True
        thread.run()

    def run_pooling(self):
        self.polling(none_stop=True, interval=0)
