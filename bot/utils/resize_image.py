import io
import re
from PIL import Image


def parse_dimensions(text: str, original_w: int, original_h: int) -> tuple[int, int]:
    text = text.strip().lower()

    percent_match = re.match(r"^(\d+)\s*%$", text)
    if percent_match:
        pct = int(percent_match.group(1))
        if not (1 <= pct <= 500):
            raise ValueError("Percentage must be between 1% and 500%.")
        return int(original_w * pct / 100), int(original_h * pct / 100)

    dim_match = re.match(r"^(\d+)\s*[x×]\s*(\d+)$", text)
    if dim_match:
        w, h = int(dim_match.group(1)), int(dim_match.group(2))
        if w < 1 or h < 1 or w > 10000 or h > 10000:
            raise ValueError("Dimensions must be between 1 and 10000 pixels.")
        return w, h

    raise ValueError("Format not recognised. Use 800x600 or 50%.")


def resize_image(image_bytes: bytes, width: int, height: int) -> tuple[bytes, int, int, int, int]:
    img = Image.open(io.BytesIO(image_bytes))
    orig_w, orig_h = img.size

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    resized = img.resize((width, height), Image.LANCZOS)

    output = io.BytesIO()
    resized.save(output, format="JPEG", quality=92)
    output.seek(0)
    return output.read(), orig_w, orig_h, width, height
