import io
from PIL import Image


def compress_image(image_bytes: bytes, quality: int = 40, max_width: int = 1280) -> tuple[bytes, int, int]:
    img = Image.open(io.BytesIO(image_bytes))
    original_size = len(image_bytes)

    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    fmt = img.format or "JPEG"
    if fmt not in ("JPEG", "PNG", "WEBP"):
        fmt = "JPEG"

    if fmt == "JPEG":
        img = img.convert("RGB")

    output = io.BytesIO()
    if fmt == "PNG":
        img.save(output, format="PNG", optimize=True)
    else:
        img.save(output, format=fmt, quality=quality, optimize=True)

    output.seek(0)
    compressed = output.read()
    return compressed, original_size, len(compressed)
