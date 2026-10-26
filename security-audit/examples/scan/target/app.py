"""Example scan target: an upload endpoint that re-encodes images (fixture, not product code)."""

import io

from PIL import Image

UPLOAD_LIMIT = 100 * 1024 * 1024


def handle_upload(body: bytes) -> bytes:
    if len(body) > UPLOAD_LIMIT:
        raise ValueError("upload too large")
    buffer = io.BytesIO()
    Image.open(io.BytesIO(body)).convert("RGB").save(buffer, "PNG")
    return buffer.getvalue()
