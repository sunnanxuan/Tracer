import random
import string
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def check_code():
    characters = string.ascii_letters + string.digits
    captcha_text = ''.join(random.choice(characters) for _ in range(5))

    char_count = len(captcha_text)
    char_width = 24
    width = 20 + (char_count - 1) * char_width + 30
    height = 30
    image = Image.new('RGB', (width, height), (255, 255, 255))
    font = ImageFont.truetype('/Library/Fonts/Arial.ttf', 24)
    draw = ImageDraw.Draw(image)

    for i, char in enumerate(captcha_text):
        x = 20 + i * char_width
        y = random.randint(0, 5)
        draw.text((x, y), char, font=font,
                  fill=(random.randint(0, 150), random.randint(0, 150), random.randint(0, 150)))

    for _ in range(10):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line(((x1, y1), (x2, y2)),
                  fill=(random.randint(150, 200), random.randint(150, 200), random.randint(150, 200)), width=1)

    for _ in range(200):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=(random.randint(0, 150), random.randint(0, 150), random.randint(0, 150)))

    image = image.filter(ImageFilter.GaussianBlur(radius=0.5))

    return [image, captcha_text]

