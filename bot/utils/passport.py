import io
import cv2
import numpy as np
from PIL import Image

PASSPORT_W = 413
PASSPORT_H = 531


def generate_passport_photo(image_bytes: bytes) -> tuple[bytes, bool]:
    np_array = np.frombuffer(image_bytes, np.uint8)
    img_cv = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    if img_cv is None:
        raise ValueError("Could not decode image.")

    h, w = img_cv.shape[:2]
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
    )

    face_detected = len(faces) > 0

    if face_detected:
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        fx, fy, fw, fh = faces[0]

        face_center_x = fx + fw // 2

        crop_h = int(fh / 0.42)
        crop_w = int(crop_h * PASSPORT_W / PASSPORT_H)

        forehead_space = int(fh * 0.35)
        crop_y = fy - forehead_space
        crop_x = face_center_x - crop_w // 2

        crop_x = max(0, crop_x)
        crop_y = max(0, crop_y)

        if crop_x + crop_w > w:
            crop_x = max(0, w - crop_w)
        if crop_y + crop_h > h:
            crop_y = max(0, h - crop_h)

        crop_w = min(crop_w, w - crop_x)
        crop_h = min(crop_h, h - crop_y)

        cropped = img_cv[crop_y:crop_y + crop_h, crop_x:crop_x + crop_w]
    else:
        cx, cy, cw, ch = _center_portrait_crop(w, h)
        cropped = img_cv[cy:cy + ch, cx:cx + cw]

    resized = cv2.resize(cropped, (PASSPORT_W, PASSPORT_H), interpolation=cv2.INTER_LANCZOS4)

    resized_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(resized_rgb)

    canvas = Image.new("RGB", (PASSPORT_W, PASSPORT_H), (255, 255, 255))
    canvas.paste(pil_img, (0, 0))

    output = io.BytesIO()
    canvas.save(output, format="JPEG", quality=95)
    output.seek(0)
    return output.read(), face_detected


def _center_portrait_crop(w: int, h: int) -> tuple[int, int, int, int]:
    target_ratio = PASSPORT_W / PASSPORT_H
    if w / h > target_ratio:
        cw = int(h * target_ratio)
        ch = h
    else:
        cw = w
        ch = int(w / target_ratio)
    cx = (w - cw) // 2
    cy = (h - ch) // 2
    return cx, cy, cw, ch
