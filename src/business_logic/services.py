import asyncio
import io
import zipfile

import aiohttp
import requests

from typing import List
from src.domain.interfaces import PublicDiskClientInterface
from src.domain.models import FileResource


class FileService(PublicDiskClientInterface):
    """
    Бизнес логика сервиса
    """

    def __init__(self, disk_client: PublicDiskClientInterface):
        self.disk_client = disk_client

    async def list_files(self, public_key: str) -> List[FileResource]:
        """
        Вызывает функцию для получения списка с сервиса (disk_client)
        """

        return await self.disk_client.get_files_list(public_key)

    @staticmethod
    async def download_file(session: aiohttp.ClientSession, url: str) -> bytes:
        """
        Асинхронно скачивает файл по указанному URL и возвращает его содержимое как байты
        """
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.read()


    async def create_files_archive(self, public_key: str, file_paths: List[str]) -> io.BytesIO:
        """
        Скачивает несколько файлов по путям и создает ZIP-архив.
        Возвращает объект BytesIO с архивом.
        """
        zip_buffer = io.BytesIO()
        async with aiohttp.ClientSession() as session:
            tasks = []
            for file_path in file_paths:
                try:
                    # Получаем прямую ссылку на скачивание
                    download_url = await self.disk_client.get_download_url(public_key, file_path)
                    tasks.append(self.download_file(session, download_url))
                except Exception as e:
                    print(f"Ошибка при получении ссылки для {file_path}: {e}")
                    tasks.append(asyncio.sleep(0))  # Пустой результат при ошибке

            # Выполняем все скачивания параллельно
            files_content = await asyncio.gather(*tasks, return_exceptions=True)

            # Архивируем файлы
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for idx, content in enumerate(files_content):
                    if isinstance(content, Exception):
                        print(f"Ошибка при скачивании {file_paths[idx]}: {content}")
                    else:
                        file_name = file_paths[idx].split("/")[-1]
                        zip_file.writestr(file_name, content)

        zip_buffer.seek(0)
        return zip_buffer