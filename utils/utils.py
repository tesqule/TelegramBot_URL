import ssl
from pathlib import Path
import re
import aiohttp
import aiofiles
import os


DOWNLOAD_FOLDER = Path("downloads")
user_history = {}  # История скачанных файлов для каждого пользователя
message_history = {}  # История сообщений для пользователей

# Инициализация бота и диспетчера
ssl_context = ssl.create_default_context()  # SSL для aiohttp

# Убедимся, что папка для загрузок существует
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

async def download_file(url: str) -> str:
    try:
        # Получаем имя файла из URL
        filename = url.split("/")[-1]
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    # Скачиваем файл
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(await response.read())
                    return filename
                else:
                    return None
    except Exception as e:
        print(f"Ошибка при скачивании файла: {e}")
        return None
# Функция для безопасного формирования имени файла
def safe_filename(url: str) -> str:
    # Функция для безопасного формирования имени файла из URL.
    filename = url.split("/")[-1]
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return filename