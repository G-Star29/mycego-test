from typing import Protocol, List
from .models import FileResource


class PublicDiskClientInterface(Protocol):
    async def get_files_list(self, public_key: str) -> List[FileResource]:
        """Возвращает список файлов по публичному ключу."""

    async def get_download_url(self, public_key: str, file_path: str) -> str:
        """Возвращает прямую ссылку для скачивания файла по пути."""