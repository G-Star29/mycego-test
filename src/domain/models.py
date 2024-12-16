from dataclasses import dataclass
from typing import Optional

@dataclass
class FileResource:
    name: str
    path: str
    mime_type: Optional[str]
    size: int

