import base64
import io

import requests
import fitz  # PyMuPDF
from PIL import Image

from app.utils.files import save_upload
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)

class DocumentIngestionService:
    def save_and_extract(self, filename: str, content: bytes, mime_type: str) -> tuple[str, str | None]:
        path = save_upload(content, filename)
        extracted = self._extract_from_bytes(content, mime_type, filename)
        logger.info('document saved', extra={'path': path})
        return path, extracted

    def extract_from_path(self, file_path: str, mime_type: str | None = None) -> str | None:
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
        except Exception:
            logger.exception('failed to read file for extraction')
            return None
        return self._extract_from_bytes(content, mime_type or _guess_mime(file_path), file_path)

    def _extract_from_bytes(self, content: bytes, mime_type: str | None, filename: str) -> str | None:
        if mime_type == 'text/plain' or str(filename).lower().endswith('.txt'):
            try:
                return content.decode('utf-8', errors='ignore')
            except Exception:
                return None
        if (mime_type == 'application/pdf') or str(filename).lower().endswith('.pdf'):
            return self._extract_pdf_text(content)
        if (mime_type and mime_type.startswith('image/')) or str(filename).lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
            return self._extract_image_text(content)
        return None

    def _extract_pdf_text(self, content: bytes) -> str | None:
        try:
            doc = fitz.open(stream=content, filetype='pdf')
        except Exception:
            logger.exception('failed to open PDF')
            return None
        # First try native text extraction (fast, no OCR needed).
        native_text: list[str] = []
        try:
            for page in doc:
                text = page.get_text('text')
                if text and text.strip():
                    native_text.append(text)
        except Exception:
            native_text = []
        if native_text:
            return '\n'.join(native_text)
        # Fallback to OCR if configured.
        if settings.NVIDIA_NIM_API_KEY is None:
            logger.warning('NVIDIA NIM API key not configured; skipping PDF OCR')
            return None
        texts: list[str] = []
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            image_bytes = pix.tobytes('png')
            text = self._extract_image_text(image_bytes)
            if text:
                texts.append(text)
        return '\n'.join(texts) if texts else None

    def _extract_image_text(self, content: bytes) -> str | None:
        if settings.NVIDIA_NIM_API_KEY is None:
            logger.warning('NVIDIA NIM API key not configured; skipping image OCR')
            return None
        data_url = _image_bytes_to_data_url(content)
        if data_url is None:
            logger.warning('image too large for NVIDIA NIM OCR')
            return None
        payload = {
            "input": [
                {
                    "type": "image_url",
                    "url": data_url,
                }
            ]
        }
        headers = {
            "Authorization": f"Bearer {settings.NVIDIA_NIM_API_KEY}",
            "Accept": "application/json",
        }
        try:
            response = requests.post(settings.NVIDIA_NIM_PAGE_ELEMENTS_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
        except Exception:
            logger.exception('NVIDIA NIM OCR request failed')
            return None
        response_payload = response.json()
        logger.info('NVIDIA NIM OCR response %s', response_payload)
        return _extract_text_from_nvidia_response(response_payload)

def _image_bytes_to_data_url(content: bytes) -> str | None:
    try:
        image = Image.open(io.BytesIO(content))
    except Exception:
        logger.exception('failed to open image')
        return None
    image = image.convert('RGB')
    for scale in (1.0, 0.75, 0.6, 0.5, 0.4, 0.3):
        if scale != 1.0:
            new_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
            resized = image.resize(new_size, Image.LANCZOS)
        else:
            resized = image
        buffer = io.BytesIO()
        resized.save(buffer, format='PNG', optimize=True)
        image_b64 = base64.b64encode(buffer.getvalue()).decode('ascii')
        if len(image_b64) < 180_000:
            return f"data:image/png;base64,{image_b64}"
    return None


def _guess_mime(file_path: str) -> str | None:
    lower = file_path.lower()
    if lower.endswith('.pdf'):
        return 'application/pdf'
    if lower.endswith('.txt'):
        return 'text/plain'
    if lower.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
        ext = lower.rsplit('.', 1)[-1]
        return f'image/{ext}'
    return None

def _extract_text_from_nvidia_response(payload: dict) -> str | None:
    if not isinstance(payload, dict):
        return None
    data = payload.get('data')
    if not isinstance(data, list):
        return None
    lines: list[str] = []
    for page in data:
        detections = page.get('text_detections') if isinstance(page, dict) else None
        if not isinstance(detections, list):
            continue
        items: list[tuple[float, float, str]] = []
        for det in detections:
            if not isinstance(det, dict):
                continue
            prediction = det.get('text_prediction')
            if not isinstance(prediction, dict):
                continue
            text = prediction.get('text')
            if not isinstance(text, str) or not text.strip():
                continue
            bbox = det.get('bounding_box')
            points = bbox.get('points') if isinstance(bbox, dict) else None
            if isinstance(points, list) and points:
                xs = [p.get('x', 0.0) for p in points if isinstance(p, dict)]
                ys = [p.get('y', 0.0) for p in points if isinstance(p, dict)]
                x_center = sum(xs) / len(xs) if xs else 0.0
                y_center = sum(ys) / len(ys) if ys else 0.0
            else:
                x_center = 0.0
                y_center = 0.0
            items.append((y_center, x_center, text.strip()))
        items.sort()
        lines.extend(text for _, _, text in items)
    return '\n'.join(lines) if lines else None
