from aiogram import types
from asgiref.sync import sync_to_async
from tg_bot.models import Bonus
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import KeyboardBuilder

kb_choise_main_menu = [
    # [types.KeyboardButton(text="Создать игру")],
    [types.KeyboardButton(text="Профиль")],
    [types.KeyboardButton(text="Моё желание")],
    [types.KeyboardButton(text="Ссылка-приглашение в игру")],
    [types.KeyboardButton(text="Про игру Тайный Санта 🎅")]
]
main_menu = types.ReplyKeyboardMarkup(
    keyboard=kb_choise_main_menu,
    resize_keyboard=True,)

kb_choise_menu_choise_profile = [
    [types.KeyboardButton(text="Указать почту")],
    [types.KeyboardButton(text="Имя игры")],
    [types.KeyboardButton(text="Задать свою дату")],
    [types.KeyboardButton(text="Основное меню")],

]
menu_profile = types.ReplyKeyboardMarkup(
    keyboard=kb_choise_menu_choise_profile,
    resize_keyboard=True,)

kb_choise_main_menu_pm = [
    [types.KeyboardButton(text="Создать игру")],
    [types.KeyboardButton(text="Просмотр пожеланий")],
    [types.KeyboardButton(text="Провести игру")],
    [types.KeyboardButton(text="Заблокировать пользователя")],
    [types.KeyboardButton(text="Оповестить участников")],
    [types.KeyboardButton(text="Основное меню")],
]
main_menu_pm = types.ReplyKeyboardMarkup(
    keyboard=kb_choise_main_menu_pm,
    resize_keyboard=True,)

kb_choise_cancel_menu = [
    [types.KeyboardButton(text="Отмена")],
]
cancel_menu = types.ReplyKeyboardMarkup(
    keyboard=kb_choise_cancel_menu,
    resize_keyboard=True,)


async def get_budget():
#     budget = await sync_to_async(Bonus.objects.all().order_by)('game_bonus')
#     builder = KeyboardBuilder(button_type=KeyboardButton)
#     budget_buttons = []
#     async for bonus in budget:
#         budget_button = KeyboardButton(text=str(bonus.game_bonus), callback_data=f'bonus_{bonus.pk}')
#         budget_buttons.append(budget_button)
#     builder.row(*budget_buttons, width=3)
#     return ReplyKeyboardMarkup(keyboard=builder.export())
    budget = await sync_to_async(Bonus.objects.all().order_by)('game_bonus')
    builder = KeyboardBuilder(button_type=InlineKeyboardButton)
    budget_buttons = []
    async for bonus in budget:
        budget_button = InlineKeyboardButton(text=str(bonus.game_bonus), callback_data=f'bonus_{bonus.pk}')
        budget_buttons.append(budget_button)
    builder.row(*budget_buttons, width=3)
    return InlineKeyboardMarkup(inline_keyboard=builder.export())
