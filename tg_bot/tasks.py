import collections
from datetime import date

from celery import shared_task
from django.core.mail import send_mail
from environs import Env
from telebot import TeleBot

from .models import UserSantaGame, Game
from secret_santa.settings import EMAIL_HOST_USER

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
                    send_notification(user, users[number + 1])
                    if user.email:
                        send_email(user)
                else:
                    user.partner = users[0]
                    user.save()
                    send_notification(user, users[0])
                    if user.email:
                        send_email(user)


@shared_task
def send_notification(sender, receiver):
    message = f'Вы дарите подарок игроку {receiver.first_name}, ' \
              f'данный игрок желает {receiver.my_wish}'
    bot.send_message(sender.telegram_id, message)


@shared_task
def send_email(user):
    subject = 'Уведомление о результатах прошедшей жребьевки'
    sender = EMAIL_HOST_USER
    emails = [user.partner.email]
    send_mail(
        subject=subject,
        message=f'Вы дарите подарок игроку {user.partner.first_name} '
                f'данный игрок желает {user.partner.my_wish}',
        from_email=sender,
        recipient_list=emails
    )
    return emails
