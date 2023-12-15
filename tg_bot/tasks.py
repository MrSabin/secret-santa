import collections
from datetime import date

from celery import shared_task
from environs import Env
from telebot import TeleBot

from .models import UserSantaGame, Game

env = Env()
bot = TeleBot(token=env.str('TG_BOT_API'), threaded=False)


@shared_task
def start_game():

    promos = [game.promo_key for game in
              Game.objects.filter(end_game=date.today())]

    if promos:
        users_by_promo = collections.defaultdict(list)
        for promo in promos:
            users_by_promo[promo].extend(list(
                UserSantaGame.objects.filter(
                    my_game__promo_key=promo, is_game_start=False)))

        for users in users_by_promo.values():
            for number, user in enumerate(users):
                if number + 1 < len(users):
                    user.partner = users[number + 1]
                    user.save()
                    send_notification(users[number + 1])
                else:
                    user.partner = users[0]
                    user.save()
                    send_notification(users[0])


@shared_task
def send_notification(user):
    message = f'Вы дарите подарок игроку {user.first_name}, ' \
              f'данный игрок желает {user.my_wish}'
    print('до отправки')
    bot.send_message(user.telegram_id, message)
    print('после отправки')
