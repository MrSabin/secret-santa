from aiogram import types


kb_choise_main_menu = [
    [types.KeyboardButton(text="Создать игру")],
    [types.KeyboardButton(text="Настройки игры")],
    [types.KeyboardButton(text="Указать ПРОМО")],
    [types.KeyboardButton(text="Ссылка-приглашение в игру")],
    [types.KeyboardButton(text="Об игре Тайный Санта...")]
]
main_menu = types.ReplyKeyboardMarkup(
    keyboard=kb_choise_main_menu,
    resize_keyboard=True,)

kb_choise_main_menu_pm = [
    [types.KeyboardButton(text="Провести игру")],
    [types.KeyboardButton(text="Заблокировать пользователя")],
    [types.KeyboardButton(text="Оповестить участников")],
    [types.KeyboardButton(text="Основное меню")],
]
main_menu_pm = types.ReplyKeyboardMarkup(
    keyboard=kb_choise_main_menu_pm,
    resize_keyboard=True,)
