from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Инлайн меню (с кнопками)
inline_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Скачать файл по URL", callback_data="download_file")],
        [InlineKeyboardButton(text="История скачанных файлов", callback_data="history")],
        [InlineKeyboardButton(text="Помощь", callback_data="help")],
        [InlineKeyboardButton(text="Информация о боте", callback_data="info")],
        [InlineKeyboardButton(text="Контакты", callback_data="contacts")],
        [InlineKeyboardButton(text="Назад", callback_data="back")]  # Кнопка назад
    ]
)
