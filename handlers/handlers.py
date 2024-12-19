from aiogram import F, Bot, types,Router
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU
from keyboard.keyboard import inline_menu_kb
from utils.utils import message_history, user_history, DOWNLOAD_FOLDER, safe_filename, ssl_context
from config_data.config import Config, load_config
import aiofiles
import aiohttp
from aiogram.types.input_file import FSInputFile
import os


config: Config = load_config()
bot = Bot(token=config.tg_bot.token)
router = Router()

# Обработка команды /start
@router.message(F.text == "/start")
async def start(message: Message):
    # Отправляем приветствие и меню с инлайн кнопками
    sent_message = await message.answer(
        text=LEXICON_RU['/start'],
        reply_markup=inline_menu_kb
    )

    # Сохраняем идентификатор отправленного сообщения
    message_history[message.from_user.id] = sent_message.message_id


# Обработка нажатия на инлайн кнопку "Скачать файл по URL"
@router.callback_query(F.data == "download_file")
async def ask_for_url(callback_query: types.CallbackQuery):
    # Запрос URL для скачивания файла.
    # Удаляем предыдущее сообщение, которое не является меню
    user_id = callback_query.from_user.id
    if user_id in message_history:
        message_to_delete = await bot.delete_message(user_id, message_history[user_id])

    # Отправляем новый запрос URL
    sent_message = await callback_query.message.answer(
        "Введите URL файла, который вы хотите скачать:"
    )

    # Сохраняем идентификатор отправленного сообщения
    message_history[user_id] = sent_message.message_id


# Обработка нажатия на инлайн кнопку "История скачанных файлов"
@router.callback_query(F.data == "history")
async def show_history(callback_query: types.CallbackQuery):
    #Отображение истории скачанных файлов для пользователя.
    user_id = callback_query.from_user.id
    history = user_history.get(user_id, [])
    if history:
        history_text = "\n".join(history)
    else:
        history_text = "Вы еще не скачивали файлы."

    # Удаляем предыдущее сообщение, которое не является меню
    if user_id in message_history:
        await bot.delete_message(user_id, message_history[user_id])

    # Отправляем историю скачанных файлов
    sent_message = await callback_query.message.answer(f"Ваша история скачанных файлов:\n{history_text}",reply_markup=inline_menu_kb)
    # Сохраняем идентификатор отправленного сообщения
    message_history[user_id] = sent_message.message_id


# Обработка нажатия на инлайн кнопку "Помощь"
@router.callback_query(F.data == "help")
async def send_help(callback_query: types.CallbackQuery):
    #Отправка информации о работе бота.
    # Удаляем предыдущее сообщение, которое не является меню
    user_id = callback_query.from_user.id
    if user_id in message_history:
        await bot.delete_message(user_id, message_history[user_id])

    # Отправляем помощь
    sent_message = await callback_query.message.answer(text=LEXICON_RU['/help'],reply_markup=inline_menu_kb)
    # Сохраняем идентификатор отправленного сообщения
    message_history[user_id] = sent_message.message_id


# Обработка нажатия на инлайн кнопку "Информация о боте"
@router.callback_query(F.data == "info")
async def bot_info(callback_query: types.CallbackQuery):
    #Отправка информации о боте.
    # Удаляем предыдущее сообщение, которое не является меню
    user_id = callback_query.from_user.id
    if user_id in message_history:
        await bot.delete_message(user_id, message_history[user_id])

    # Отправляем информацию о боте
    sent_message = await callback_query.message.answer(text=LEXICON_RU['info'],reply_markup=inline_menu_kb)
    # Сохраняем идентификатор отправленного сообщения
    message_history[user_id] = sent_message.message_id


# Обработка нажатия на инлайн кнопку "Контакты"
@router.callback_query(F.data == "contacts")
async def bot_contacts(callback_query: types.CallbackQuery):
    #Отправка контактной информации.
    # Удаляем предыдущее сообщение, которое не является меню
    user_id = callback_query.from_user.id
    if user_id in message_history:
        await bot.delete_message(user_id, message_history[user_id])

    # Отправляем контактную информацию
    sent_message = await callback_query.message.answer(text=LEXICON_RU['contacts'],reply_markup=inline_menu_kb)
    # Сохраняем идентификатор отправленного сообщения
    message_history[user_id] = sent_message.message_id


# Обработка нажатия на инлайн кнопку "Назад"
@router.callback_query(F.data == "back")
async def go_back(callback_query: types.CallbackQuery):
    # Возвращение в главное меню и удаление старого сообщения.
    # Удаляем старое сообщение, которое не является меню
    user_id = callback_query.from_user.id
    if user_id in message_history:
        await bot.delete_message(user_id, message_history[user_id])

    # Отправляем новое сообщение с меню
    sent_message = await callback_query.message.answer(
        "Привет! Я бот для скачивания файлов по URL.\n"
        "Что я могу для вас сделать?\n\n"
        "Выберите одну из опций:",
        reply_markup=inline_menu_kb
    )
    # Сохраняем идентификатор отправленного сообщения
    message_history[user_id] = sent_message.message_id

# Обработка URL и скачивание файла
@router.message(F.text.regexp(r'^https?://'))
async def download_file(message: Message):
    """Загрузка файла по URL и сохранение его на сервере."""
    url = message.text
    filename = safe_filename(url)  # Используем безопасное имя файла
    filepath = DOWNLOAD_FOLDER / filename

    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    # Получаем содержимое файла
                    file_content = await response.read()
                    if file_content:
                        # Сохраняем файл асинхронно
                        async with aiofiles.open(filepath, 'wb') as f:
                            await f.write(file_content)

                        # Добавление в историю скачивания
                        user_id = message.from_user.id
                        if user_id not in user_history:
                            user_history[user_id] = []
                        user_history[user_id].append(f"Файл: {filename}, Путь: {str(filepath)}")

                        # Отправляем уведомление о скачанном файле
                        document = FSInputFile(filepath)
                        await bot.send_document(user_id, document, caption=f"Файл успешно скачан: {filename}",
                                                reply_markup=inline_menu_kb
                                                )
                        os.remove(filepath)

                    else:
                        await message.answer("Не удалось скачать файл. Файл пустой.")
                else:
                    await message.answer(f"Не удалось скачать файл. Статус: {response.status}. Проверьте URL.")
    except Exception as e:
        await message.answer(f"Ошибка при скачивании: {e}")
