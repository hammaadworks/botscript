# /// script
# dependencies = [
#   "opencv-python",
#   "easyocr",
#   "numpy",
#   "pyautogui",
#   "pillow",
# ]
# ///

import time

import cv2
import easyocr
import numpy as np
import pyautogui as pag
from PIL import Image

import os
import tempfile

IMAGE_PATH = os.path.join(tempfile.gettempdir(), "ztype.jpg")
"""str: The path to the image file used for OCR."""

skip_words = ['ztype', 'new game', 'settings', 'my stats',
              'phoboslab', 'load your own text', 'wave', 'score']
"""list[str]: A list of words to skip during OCR processing."""

PREV_RESULT = list()
"""list[str]: A list to store the previous OCR result."""

RESIZE_RATIO = (500, 800)
"""tuple[int, int]: The desired width and height for resizing the image."""
PAUSE_BUTTON = (375, 405)
"""tuple[int, int]: The x and y coordinates of the pause button in the game."""
RESUME_BUTTON = (800, 1390)
"""tuple[int, int]: The x and y coordinates of the resume button in the game."""
GAME_SCREEN = (800, 800)
"""tuple[int, int]: The x and y coordinates to click within the game screen."""
PYCHARM_SCREEN = (3000, 800)
"""tuple[int, int]: The x and y coordinates to click within the PyCharm screen."""
ENGLISH_ALPHA = "thequickbrownfoxjumpedoverthelazydog"
"""str: A string containing all lowercase English letters, used as a fallback."""


def resize_image():
    """Resizes the image located at `IMAGE_PATH` to `RESIZE_RATIO`.

    This function opens the image at `IMAGE_PATH`, resizes it to the dimensions
    specified by `RESIZE_RATIO` using anti-aliasing, and then saves the resized
    image back to the same path. It also prints the original and resized dimensions
    to the console for debugging purposes.

    """
    foo = Image.open(IMAGE_PATH)
    print(f"Size of screenshot= {foo.size}")
    foo = foo.resize(RESIZE_RATIO, Image.Resampling.LANCZOS)
    foo.save(IMAGE_PATH, optimize=True, quality=95)
    foo = Image.open(IMAGE_PATH)
    print(f"Size of resized screenshot= {foo.size}")


def get_ocr_result(prev_result):
    """Performs OCR on the image at `IMAGE_PATH`, returning a list of words.

    This function pauses the game, uses EasyOCR to extract text from the image,
    filters out words in `skip_words`, sorts the results by length, and handles
    a "stuck letter" scenario. It then resumes the game and prints the result.

    Args:
        prev_result (list[str]): The previous OCR result, used to detect stuck letters.

    Returns:
        list[str]: A list of extracted words from the image.
    """
    # pause the game
    print(f'Pausing the game....')
    pag.click(PAUSE_BUTTON[0], PAUSE_BUTTON[1])
    reader = easyocr.Reader(['en'], detector='dbnet18')
    result = reader.readtext(IMAGE_PATH, detail=0, batch_size=8)
    result = [block.lower() for block in result if not block.lower().startswith(tuple(skip_words))]
    result.sort(key=len)

    # stuck letter
    if len(prev_result):
        prev_result.sort(key=len, reverse=True)
    for prev_word in prev_result:
        if prev_word in result:
            result.clear()
            result.append(ENGLISH_ALPHA)

    pag.click(RESUME_BUTTON[0], RESUME_BUTTON[1])
    print(f'Resume and Typing this: {result}')
    return result


def transform_image_colour():
    """Transforms the colors in the image at `IMAGE_PATH`.

    This function reads the image using OpenCV, sets all pixels with RGB values
    less than [100, 100, 100] to black ([0, 0, 0]), and sets all pixels with RGB
    values greater than or equal to [100, 100, 100] to white ([225, 225, 225]).
    The modified image is then saved back to the same path. A confirmation
    message is printed to the console.
    """
    img = cv2.imread(IMAGE_PATH)
    img[np.where((img < [100, 100, 100]).all(axis=2))] = [0, 0, 0]
    img[np.where((img >= [100, 100, 100]).all(axis=2))] = [225, 225, 225]
    cv2.imwrite(IMAGE_PATH, img)
    print("Completed color transformations")


while True:
    """The main loop for the Z-Type game bot.

    This loop continuously takes screenshots of the game, processes them
    for OCR, and then types the extracted words. It uses `pyautogui` to
    interact with the game. The loop includes pauses, screen captures,
    image resizing and color transformation, and text typing.
    """
    pag.press('space')
    im = pag.screenshot(region=(325, 355, 950, 1430), imageFilename=IMAGE_PATH)
    resize_image()
    transform_image_colour()
    pag.click(GAME_SCREEN[0], GAME_SCREEN[1])
    pag.click(PYCHARM_SCREEN[0], PYCHARM_SCREEN[1])
    pag.click(GAME_SCREEN[0], GAME_SCREEN[1])
    ocr_result = get_ocr_result(PREV_RESULT)
    PREV_RESULT = ocr_result
    for word in ocr_result:
        pag.write(word)
        print(f'Typed word: {word}')
        time.sleep(0.25)
#
# while 1:
#     print(pag.position())