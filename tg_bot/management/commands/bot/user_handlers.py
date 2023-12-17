from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StatesGroup, State
import logging
from aiogram.methods.get_me import GetMe
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from environs import Env
from tg_bot.models import *
from tg_bot.management.commands.bot.user_menu import *
import dateutil.parser as dp

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d - %(levelname)-8s - %(asctime)s - %(funcName)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

env: Env = Env()
env.read_env()

bot: Bot = Bot(token=env('TG_BOT_API'), parse_mode='HTML')

router = Router()


class GameStateEmail(StatesGroup):
    email_game = State()

class GameStateEmail(StatesGroup):
    email_game = State()


class GameStateName(StatesGroup):
    name_game = State()


class GameMyWish(StatesGroup):
    my_wish = State()


class SetDate(StatesGroup):
    date = State()


@router.message(Command(commands=["start"]))
async def start_command_handler(message: Message):
    promo_candidate = ''
    find_game = None
    user_id = await sync_to_async(UserSantaGame.objects.filter(
        telegram_id=int(message.from_user.id)).first)()
    if " " in message.text:
        promo_candidate = message.text.split()[1]
        find_game = await sync_to_async(
            Game.objects.filter(
                promo_key=str(promo_candidate).upper()).first)()

    if not user_id:
        # если есть промо - находим игру и добавить к пользователю его игру
        user_id = UserSantaGame(telegram_id=int(message.from_user.id),
                                first_name=message.from_user.first_name,
                                my_game=find_game)
        await sync_to_async(user_id.save)()
        if not find_game:
            await bot.send_message(
                message.from_user.id,
                f'Привет {message.from_user.first_name}, создай игру🎅\n'
                f'Организуй тайный обмен подарками, '
                f'запусти праздничное настроение! 🎄', reply_markup=main_menu)
        else:
            await bot.send_message(
                message.from_user.id,
                f'Привет {message.from_user.first_name}, '
                f'ты в игре\n\'{str(find_game.info)}\'\nДата проведения '
                f'{str(find_game.end_game)}', reply_markup=main_menu)
    else:
        if await sync_to_async(Assistant.objects.filter(telegram_id=int(message.from_user.id)).first)():
        # это Асистент игр
            await bot.send_message(
                message.from_user.id,
                f'Привет, {message.from_user.first_name}, '
                f'ты супер администратор игры Санта 🎅\nМожешь при '
                f'желании создать новую игру',
                reply_markup=main_menu_pm)
        else:
            # это обычный юзер и был ранее в боте, но зашел повторно,
            # если по промо, то обновить его запись на эту промо
            if find_game:
                await sync_to_async(UserSantaGame.objects.filter(
                    id=user_id.id).update)(my_game=find_game)
                await bot.send_message(
                    message.from_user.id,
                    f'Привет ☃️{message.from_user.first_name}\n'
                    f'Рад снова видеть тебя, но теперь ты в игре Тайный-Санта'
                    f'!!!\n\'{str(find_game.info)}\'\nДата проведения '
                    f'{str(find_game.end_game)}',
                    reply_markup=main_menu)
            else:
                await bot.send_message(
                    message.from_user.id,
                    f'Привет {message.from_user.first_name}, '
                    f'pад снова видеть тебя\nМожешь при желании создать новую'
                    f' игру и пригласить своих знакомых',
                    reply_markup=main_menu)


@router.message(F.text == "Основное меню")
async def show_main_menu(message: Message):
    await bot.send_message(
        message.from_user.id,
        'и снова привет от 🎅',
        reply_markup=main_menu)


@router.message(F.text == "Провести игру")
async def run_game(message: Message):
    await bot.send_message(message.from_user.id,
                           F.text,
                           reply_markup=main_menu)


@router.message(F.text == "Создать игру")
async def run_game(message: Message):
    await bot.send_message(message.from_user.id, 'Укажите бюджет игры',
                               reply_markup=await get_budget())


@router.callback_query(F.data.startswith('bonus_'))
# @router.callback_query(F.data.startswith('bonus_'))
async def get_bonus_handler(callback: CallbackQuery):
    bonus_id = callback.data.split('_')[-1]
    user_id = await sync_to_async(UserSantaGame.objects.filter(
        telegram_id=int(callback.from_user.id)).first)()
    if user_id.is_game_start:
        await bot.send_message(
            callback.from_user.id,
            f"У вас игра Тайный-Санта - уже создана!",
            reply_markup=main_menu)
    else:
        bot_name = await bot(GetMe())
        budget = await sync_to_async(Bonus.objects.filter(
            id=bonus_id).first)()
        new_game = Game(
            bonus=budget,
            info='Игра Тайный-Санта 🎅',
            end_game=datetime(
                year=datetime.now().year,
                month=12,
                day=30))
        await sync_to_async(new_game.save)()
        game_promo_key = new_game.promo_key
        await sync_to_async(UserSantaGame.objects.filter(
            id=user_id.id).update)(my_game=new_game, is_game_start=True)
        await bot.send_message(
            callback.from_user.id,
            f"Ваша игра Тайный-Санта-создана, ссылка для участия\n"
            f"https://t.me/{bot_name.username}?start={game_promo_key}",
            reply_markup=main_menu)


@router.message(F.text == "Заблокировать пользователя")
async def user_block(message: Message):
    await bot.send_message(
        message.from_user.id,
        F.text,
        reply_markup=main_menu)


@router.message(F.text == "Профиль")
async def user_block(message: Message):
    await bot.send_message(
        message.from_user.id,
        "Дополнительные настройки",
        reply_markup=menu_profile)


@router.message(Command("Отмена"))
@router.message(F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer("Отмена действий", reply_markup=menu_profile,)


@router.message(F.text == "Моё желание")
async def user_block(message: Message, state: FSMContext):
    await state.set_state(GameMyWish.my_wish)
    await message.answer(
        "Запишите ваше желание😉!\nИ кто знает! Может оно исполниться",
        reply_markup=cancel_menu)


@router.message(GameMyWish.my_wish)
async def process_my_wish(message: Message, state: FSMContext) -> None:
        data = await state.update_data(my_wish=message.text)
        await state.clear()
        my_wish = data.get("my_wish", "<something unexpected>")
        current_user = await sync_to_async(
            UserSantaGame.objects.filter(
                telegram_id=int(message.from_user.id)).first)()
        await sync_to_async(UserSantaGame.objects.filter(
            id=current_user.id).update)(my_wish=my_wish)
        await bot.send_message(
            message.from_user.id,
            f'Санта обязательно его прочитает 🎅 ',
            reply_markup=main_menu)


@router.message(F.text == "Имя игры")
async def user_block(message: Message, state: FSMContext):
    await state.set_state(GameStateName.name_game)
    await message.answer(
        "Задайте наименование вашей игры !",
        reply_markup=cancel_menu)


@router.message(GameStateName.name_game)
async def process_email(message: Message, state: FSMContext) -> None:
        data = await state.update_data(name_game=message.text)
        await state.clear()
        name_game = data.get("name_game", "<something unexpected>")
        current_user = await sync_to_async(
            UserSantaGame.objects.filter(
                telegram_id=int(message.from_user.id)).first)()
        if current_user.is_game_start:
            await sync_to_async(Game.objects.filter(
                id=current_user.my_game_id).update)(info=name_game)
            await bot.send_message(
                message.from_user.id,
                f'Успешно 🤝 ',
                reply_markup=main_menu)
        else:
            await bot.send_message(
                message.from_user.id,
                f'Нет активных игр, создайте новую! '
                f'или используйте ПРОМО код',
                reply_markup=main_menu)


@router.message(F.text == "Указать почту")
async def user_block(message: Message, state: FSMContext):
    await state.set_state(GameStateEmail.email_game)
    await message.answer("Укажите вашу почту!", reply_markup=cancel_menu)


@router.message(GameStateEmail.email_game)
async def process_email(message: Message, state: FSMContext) -> None:
        data = await state.update_data(email_game=message.text)
        await state.clear()
        email = data.get("email_game", "<something unexpected>")
        current_user = await sync_to_async(UserSantaGame.objects.filter(
            telegram_id=int(message.from_user.id)).first)()
        await sync_to_async(UserSantaGame.objects.filter(
            id=current_user.id).update)(email=email)
        await bot.send_message(
            message.from_user.id,
            f'Успешно 🤝 ',
            reply_markup=main_menu)


@router.message(F.text == "Ссылка-приглашение в игру")
async def link_to_game(message: Message):
    bot_name = await bot(GetMe())
    user_id = await sync_to_async(UserSantaGame.objects.filter(
        telegram_id=int(message.from_user.id)).first)()
    promo = await sync_to_async(Game.objects.filter(
        id=user_id.my_game_id).first)()
    if promo:
        await bot.send_message(
            message.from_user.id,
            f'Отправляй ссылку-приглашение своим знакомым для участия в '
            f'игре\nТайный Санта 🎅\n\nhttps://t.me/{bot_name.username}?start='
            f'{str(promo.promo_key)}', reply_markup=main_menu)
    else:
        await bot.send_message(
            message.from_user.id,
            f'Активной игры не существует‼️\nВы можете создать новую...',
            reply_markup=main_menu)


@router.message(F.text == "Оповестить участников")
async def show_main_menu(message: Message):
    async for user in UserSantaGame.objects.all().order_by('telegram_id'):
        try:
            await bot.send_message(
                str(user.telegram_id),
                f'Проверка рассылки и т.д...')
        except TelegramBadRequest:
            await bot.send_message(
                message.from_user.id,
                f'Пользователь телеграмм {str(user.telegram_id)} '
                f'не существует')


@router.message(F.text == "Просмотр пожеланий")
async def view_wish(message: Message):
    current_user = await sync_to_async(UserSantaGame.objects.filter(
        telegram_id=int(message.from_user.id)).first)()
    if current_user.is_game_start:
        game = await sync_to_async(Game.objects.filter(
            id=current_user.my_game_id).first)()
        wishes = []
        wishes.append(f'Списки желаний участников игры Тайный Санта\n')
        async for wish in UserSantaGame.objects.all():
            if wish.my_wish:
                wishes.append(f'{wish.my_wish}')
        wish_list = '\n'.join(wishes)
        await message.answer(wish_list)
    else:
        await message.answer(
            'К сожалению, список желаний участников игры вам не доступен...')


@router.message(F.text == "Про игру Тайный Санта 🎅")
async def about_game(message: Message):
    current_user = await sync_to_async(UserSantaGame.objects.filter(telegram_id=int(message.from_user.id)).first)()
    current_game = await sync_to_async(Game.objects.filter(id=current_user.my_game_id).first)()
    if(current_game):
        bonus_game = await sync_to_async(Bonus.objects.filter(id=current_game.bonus_id).first)()
        bonus_dict = {}
        for tuple in list(bonus_game.BONUS_CHOICES):
            bonus_dict[tuple[0]] = tuple[1]
        info = f'😉 Игра Тайный Санта 🎅\n\n'\
            f'{current_game.info}\n'\
            f'Дата проведения игры {current_game.end_game}\n'\
            f'ПРОМО-КЛЮЧ {current_game.promo_key}\n'\
            f'Бюджет игры {bonus_dict[bonus_game.game_bonus]}\n'\
            f'Участник {current_user.first_name}\n'\
            f'Почта для оповещения {current_user.email}\n'\
            f'Вы Создатель игры ? -> {current_user.is_game_start}\n'
        await message.answer(info)
    else:
        await message.answer("Необходимо создать игру или активировать её по промокоду...")


@router.message(F.text =='Задать свою дату')
async def set_data(message: Message, state: FSMContext):
    await state.set_state(SetDate.date)
    await message.answer("Укажите дату проведения игры вида ДД.ММ.ГГГГ !", reply_markup=cancel_menu)

@router.message(SetDate.date)
async def process_email(message: Message, state: FSMContext) -> None:
        data = await state.update_data(date=message.text)
        await state.clear()
        new_date = data.get("date", "<something unexpected>")
        try:
            new_date = dp.parse(new_date)
            current_user = await sync_to_async(UserSantaGame.objects.filter(telegram_id=int(message.from_user.id)).first)()
            if current_user.is_game_start:
                await sync_to_async(Game.objects.filter(id=current_user.my_game_id).update)(end_game=new_date)
                await bot.send_message(message.from_user.id, f'Успешно 🤝 ', reply_markup=main_menu)
            else:
                await bot.send_message(message.from_user.id, f'Только создатель игры может менять дату 🛑', reply_markup=main_menu)
        except ValueError:
            await bot.send_message(message.from_user.id, f'Не верно задана дата 🛑', reply_markup=main_menu)
