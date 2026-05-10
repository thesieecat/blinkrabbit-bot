from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

BTN_PDF = "Image to PDF"
BTN_COMPRESS = "Compress Image"
BTN_QR = "QR Generator"
BTN_PASSPORT = "Passport Photo"
BTN_RESIZE = "Resize Image"
BTN_HELP = "Help"
BTN_GENERATE_PDF = "Generate PDF"
BTN_CLEAR_IMAGES = "Clear Images"
BTN_CANCEL = "Cancel"
BTN_REMOVE_BG = "Remove Background"

ALL_BUTTONS = {BTN_PDF, BTN_COMPRESS, BTN_QR, BTN_PASSPORT, BTN_RESIZE, BTN_HELP,
               BTN_GENERATE_PDF, BTN_CLEAR_IMAGES, BTN_CANCEL, BTN_REMOVE_BG}

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [BTN_PDF, BTN_COMPRESS],
        [BTN_QR, BTN_PASSPORT],
        [BTN_RESIZE, BTN_REMOVE_BG],
        [BTN_HELP],
    ],
    resize_keyboard=True,
    is_persistent=True,
)

PDF_KEYBOARD = ReplyKeyboardMarkup(
    [
        [BTN_GENERATE_PDF, BTN_CLEAR_IMAGES],
        [BTN_CANCEL],
    ],
    resize_keyboard=True,
    is_persistent=True,
)

CANCEL_KEYBOARD = ReplyKeyboardMarkup(
    [[BTN_CANCEL]],
    resize_keyboard=True,
    is_persistent=True,
)

INSTAGRAM_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("Follow on Instagram", url="https://www.instagram.com/blinkrabbit")]
])
