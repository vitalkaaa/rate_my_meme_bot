import time
from datetime import datetime, timedelta
from threading import Thread

import schedule
import telebot

from models import Meme, User, Vote


class BotEngine:
    def __init__(self):
        self.cached_last_meme_date = dict()

    def cache_last_meme_date(self, user_id):
        self.cached_last_meme_date[user_id] = datetime.utcnow()

    def get_last_meme_date(self, user_id):
        if self.cached_last_meme_date.get(user_id) is None:
            last_meme = Meme.get_last(user_id)
            if last_meme is not None:
                return last_meme.posted_at
            else:
                return datetime.utcnow() - timedelta(days=1)
        else:
            return self.cached_last_meme_date[user_id]

    def get_message_info(self, message):
        file_id = None
        file_type = None
        allowed_file = False
        msg_id = message.message_id

        back_text = 'Можно отправить одно видео, картинку или анимацию, ' \
                    'а так же репостить их из других из других каналов и групп'

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
            if file_type in ('video', 'animation'):
                allowed_file = True
                back_text = 'Сейчас опубликуем ваш мем'
            elif file_type == 'photo':
                allowed_file = True
                back_text = 'Сейчас опубликуем ваш мем'

        if datetime.utcnow() - self.get_last_meme_date(message.from_user.id) < timedelta(seconds=3):
            allowed_file = False
            back_text = 'Вы можете постить один мем раз в сутки'

        return {'allowed_file': allowed_file, 'file_id': file_id, 'file_type': file_type, 'back_text': back_text, 'msg_id': msg_id}

    def get_callback_info(self, call):
        data = call.data
        user_id = str(call.from_user.id)
        call_type = None
        mark = None
        is_voted = False
        back_text = ':)))))'

        if data.startswith('vote'):
            call_type = 'vote'
            mark = int(data.split('_')[-1])
            meme = Meme.get_by_msg_id(call.message.message_id)
            user = User.get(user_id)

            if user.id == meme.user_id:
                back_text = 'Нельзя голосовать за свой мем'
                is_voted = False
                return {'type': call_type, 'mark': mark, 'is_voted': is_voted, 'back_text': back_text}

            if self.save_vote(user_id, meme.id, mark):
                back_text = 'Вы проголосовали'
                Vote(user_id, meme.id, mark).save()
                is_voted = True
            else:
                back_text = 'Вы уже голосовали за этот мем'
                is_voted = False

        return {'type': call_type, 'mark': mark, 'is_voted': is_voted, 'back_text': back_text}

    def user_info(self, action):
        user_id = str(action.from_user.id)
        username = '@' + action.from_user.username
        fullname = str(action.from_user.first_name) + ' ' + str(action.from_user.last_name)
        fullname = fullname.replace('None', '') if fullname.replace('None', '') != '' else None
        return {'user_id': user_id, 'fullname': fullname, 'username': username}

    def save_user(self, action):
        user_info = self.user_info(action)
        user = User.get(user_info['user_id'])

        if user is None:
            user = User(user_info['user_id'], user_info['username'], user_info['fullname']).save()
            print(f'{user} registred', flush=True)
        return user

    def save_meme(self, user_id, file_type, file_id, msg_id):
        meme = Meme(user_id, file_type, file_id, msg_id).save()
        user = User.get(user_id)
        print(f'{user} have posted {meme}', flush=True)

    def save_vote(self, user_id, meme_id, mark):
        if not Vote.is_voted(user_id, meme_id):
            vote = Vote(user_id, meme_id, mark).save()
            user = User.get(user_id)
            user.add_points(mark)
            print(f'{user} marked {vote}', flush=True)
            return True
        return False

    @staticmethod
    def run_scheduler():
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
