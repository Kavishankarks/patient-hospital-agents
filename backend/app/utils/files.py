import os
from uuid import uuid4

from app.core.config import settings


def save_upload(file_bytes: bytes, filename: str) -> str:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(filename)[1]
    path = os.path.join(settings.UPLOAD_DIR, f"{uuid4().hex}{ext}")
    with open(path, 'wb') as f:
        f.write(file_bytes)
    return path
