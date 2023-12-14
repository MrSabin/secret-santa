from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StatesGroup, State
import logging
from aiogram.methods.get_me import GetMe
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.filters import Command
from asgiref.sync import sync_to_async
from environs import Env

from secret_santa.settings import BASE_DIR
from tg_bot.models import *
# from tg_bot.management.commands.bot.user_keyboards import get_catalog_keyboard
from tg_bot.management.commands.bot.user_menu import *
from aiogram.utils.keyboard import ReplyKeyboardBuilder

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d - %(levelname)-8s - %(asctime)s - %(funcName)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

env: Env = Env()
env.read_env()

bot: Bot = Bot(token=env('TG_BOT_API'), parse_mode='HTML')

router = Router()


class GameState(StatesGroup):
    game_info = State()
    game_bonus = State()


@router.message(Command(commands=["start"]))
async def start_command_handler(message: Message):
    User = await bot(GetMe())
    promo_candidate = ''
    find_game = None
    user_id = await sync_to_async(UserSantaGame.objects.filter(telegram_id=int(message.from_user.id)).first)()
    if " " in message.text:
        promo_candidate = message.text.split()[1]
        find_game = await sync_to_async(Game.objects.filter(promo_key=str(promo_candidate).upper()).first)()

    if not user_id:
        # если есть промо - находим игру и добавить к пользователю его игру
        user_id = UserSantaGame(telegram_id=int(message.from_user.id), first_name=message.from_user.first_name, my_game=find_game)
        await sync_to_async(user_id.save)()
        if not find_game:
            await bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}, создай игру🎅\nОрганизуй тайный обмен подарками, запусти праздничное настроение! 🎄', reply_markup=main_menu)
        else:
            await bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}, ты в игре\n\'{str(find_game.info)}\'\nДата проведения {str(find_game.end_game)}', reply_markup=main_menu)
    else:
        if await sync_to_async(SuperUser.objects.filter(telegram_id=int(message.from_user.id)).first)():
        # это ПМ
            await bot.send_message(message.from_user.id,
                                   f'Привет, {message.from_user.first_name}, ты супер администратор игры Санта 🎅\nМожешь при желании создать новую игру',
                                   reply_markup=main_menu_pm)
        else:
            # это обычный юзер и был ранее в боте, но зашел повторно,
            # если по промо, то обновить его запись на эту промо
            if find_game:
                await sync_to_async(UserSantaGame.objects.filter(id=user_id.id).update)(my_game=find_game)
                await bot.send_message(message.from_user.id,
                                   f'Привет ☃️{message.from_user.first_name}\nРад снова видеть тебя, но теперь ты в игре Тайный-Санта!!!\n\'{str(find_game.info)}\'\nДата проведения {str(find_game.end_game)}', reply_markup=main_menu)
            else:
                await bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}, pад снова видеть тебя\nМожешь при желании создать новую игру и пригласить своих знакомых', reply_markup=main_menu)


@router.message(F.text == "Основное меню")
async def show_main_menu(message: Message):
    await bot.send_message(message.from_user.id, 'и снова привет от 🎅', reply_markup=main_menu)


@router.message(F.text == "Провести игру")
async def run_game(message: Message):
    await bot.send_message(message.from_user.id, F.text, reply_markup=main_menu)


@router.message(F.text == "Создать игру")
async def run_game(message: Message):
    await bot.send_message(message.from_user.id, 'Укажите бюджет игры',
                               reply_markup=await get_budget())

@router.callback_query(F.data.startswith('bonus_'))
# @router.callback_query(F.data.startswith('bonus_'))
async def get_bonus_handler(callback: CallbackQuery):
    bonus_id = callback.data.split('_')[-1]
    user_id = await sync_to_async(UserSantaGame.objects.filter(telegram_id=int(callback.from_user.id)).first)()
    bot_name = await bot(GetMe())
    budget = await sync_to_async(Bonus.objects.filter(id=bonus_id).first)()
    new_game = Game(bonus=budget, info='Игра Тайный-Санта 🎅', end_game=datetime(year=datetime.now().year, month=12, day=30))
    await sync_to_async(new_game.save)()
    game_promo_key = new_game.promo_key
    await sync_to_async(UserSantaGame.objects.filter(id=user_id.id).update)(my_game=new_game, is_game_start=True)
    await bot.send_message(callback.from_user.id, f"Ваша игра Тайный-Санта-создана, ссылка для участия\nhttps://t.me/{bot_name.username}?start={game_promo_key}", reply_markup=main_menu)



@router.message(F.text == "Заблокировать пользователя")
async def user_block(message: Message):
    await bot.send_message(message.from_user.id, F.text, reply_markup=main_menu)


@router.message(F.text == "Ссылка-приглашение в игру")
async def link_to_game(message: Message):
    bot_name = await bot(GetMe())
    user_id = await sync_to_async(UserSantaGame.objects.filter(telegram_id=int(message.from_user.id)).first)()
    promo = await sync_to_async(Game.objects.filter(id=user_id.my_game_id).first)()
    if promo:
        await bot.send_message(message.from_user.id, f'Отправляй ссылку-приглашение своим знакомым для участия в игре\nТайный Санта 🎅\n\nhttps://t.me/{bot_name.username}?start={str(promo.promo_key)}', reply_markup=main_menu)
    else:
        await bot.send_message(message.from_user.id, f'Активной игры не существует‼️\nВы можете создать новую...', reply_markup=main_menu)


@router.message(F.text == "Оповестить участников")
async def show_main_menu(message: Message):
    async for user in UserSantaGame.objects.all().order_by('telegram_id'):
        try:
            await bot.send_message(str(user.telegram_id), f'Проверка рассылки и т.д...')
        except TelegramBadRequest:
            await bot.send_message(message.from_user.id, f'Пользователь телеграмм {str(user.telegram_id)} не существует')


@router.message(F.text == "Об игре Тайный Санта...")
async def create_order(message: Message):
    await message.answer('https://dvmn.org/')



