import aiohttp
from typing import List
from src.domain.interfaces import PublicDiskClientInterface
from src.domain.models import FileResource


class AsyncYandexDiskClient(PublicDiskClientInterface):

    async def get_files_list(self, public_key: str) -> List[FileResource]:
        """
        Переопределяем функцию для работы с Yandex API
        """

        url = 'https://cloud-api.yandex.net/v1/disk/public/resources'
        params = {'public_key': public_key, 'limit': 1000}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                items = data.get("_embedded", {}).get("items", [])
                return [
                    FileResource(
                        name=item["name"],
                        path=item["path"],
                        mime_type=item.get("mime_type"),
                        size=item.get("size", 0),
                    )
                    for item in items if item["type"] == "file"
                ]


    async def get_download_url(self, public_key: str, file_path: str) -> str:
        """Переопределяем функцию для работы с Yandex API"""

        url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download'
        params = {'public_key': public_key, 'path': file_path}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("href")