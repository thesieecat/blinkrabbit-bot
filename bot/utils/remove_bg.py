import io
from rembg import remove
from PIL import Image


def remove_background(image_bytes: bytes) -> bytes:
    output_bytes = remove(image_bytes)

    img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
    out = io.BytesIO()
    img.save(out, format="PNG")
    out.seek(0)
    return out.read()
