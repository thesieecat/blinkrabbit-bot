import io
from PIL import Image


def images_to_pdf(image_bytes_list: list[bytes]) -> bytes:
    images = []
    for img_bytes in image_bytes_list:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        images.append(img)

    output = io.BytesIO()
    if len(images) == 1:
        images[0].save(output, format="PDF")
    else:
        images[0].save(output, format="PDF", save_all=True, append_images=images[1:])

    output.seek(0)
    return output.read()
