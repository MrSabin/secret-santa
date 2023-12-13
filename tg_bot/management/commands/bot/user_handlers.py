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
    user_name = State()


@router.message(Command(commands=["start"]))
async def start_command_handler(message: Message):
    User = await bot(GetMe())
    referrer_candidate = ''
    if " " in message.text:
        referrer_candidate = message.text.split()[1]
        # await bot.send_message(message.from_user.id, f'Вас приветствует Санта Бот 🎁🎄⛄\nВаш промо-код {referrer_candidate}', reply_markup=main_menu)
    user_id = await sync_to_async(UserSantaGame.objects.filter(telegram_id=int(message.from_user.id)).first)()
    if not user_id:
        user_id = UserSantaGame(telegram_id=int(message.from_user.id), first_name=message.from_user.first_name)
        await sync_to_async(user_id.save)()
        await bot.send_message(message.from_user.id, f'Привет 🎅{message.from_user.first_name}\nОрганизуй тайный обмен подарками, запусти праздничное настроение! 🎄', reply_markup=main_menu)
    else:
        if await sync_to_async(SuperUser.objects.filter(telegram_id=int(message.from_user.id)).first)():
        # это ПМ
            await bot.send_message(message.from_user.id,
                                   f'Привет 🎅{message.from_user.first_name}',
                                   reply_markup=main_menu_pm)

        else:
            # это обычный юзер, но зашел повторно
            await bot.send_message(message.from_user.id,
                                   f'Привет ☃️{message.from_user.first_name}\nРад снова видеть тебя!!!',
                                   reply_markup=main_menu)


@router.message(F.text == "Основное меню")
async def show_main_menu(message: Message):
    await bot.send_message(message.from_user.id, 'и снова привет от 🎅', reply_markup=main_menu)


@router.message(F.text == "Провести игру")
async def run_game(message: Message):
    await bot.send_message(message.from_user.id, F.text, reply_markup=main_menu)


@router.message(F.text == "Заблокировать пользователя")
async def user_block(message: Message):
    await bot.send_message(message.from_user.id, F.text, reply_markup=main_menu)


@router.message(F.text == "Ссылка-приглашение в игру")
async def link_to_game(message: Message):
    bot_name = await bot(GetMe())
    # тут получить код - ПРОМО
    promo = 'Test'
    await bot.send_message(message.from_user.id, f'Отправляйте ссылку-приглашение своим знакомым для участия в игре\nТайный Санта 🎅\n\nhttps://t.me/@{bot_name.username}?start={promo}', reply_markup=main_menu)



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



