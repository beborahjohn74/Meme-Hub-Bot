"""
image_gen.py
Generates joke images: a colorful background + bold meme-style text rendered on top.
No paid APIs needed — backgrounds are drawn programmatically with Pillow.
"""

import os
import random
import textwrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "DejaVuSans-Bold.ttf")

WIDTH, HEIGHT = 1000, 1000

# A handful of pleasant gradient color pairs to rotate through.
GRADIENTS = [
    ((255, 94, 98), (255, 195, 113)),   # red -> orange
    ((94, 129, 255), (154, 94, 255)),   # blue -> purple
    ((0, 201, 167), (0, 148, 255)),     # teal -> blue
    ((255, 94, 214), (255, 154, 60)),   # pink -> orange
    ((60, 60, 90), (20, 20, 40)),       # dark slate
    ((255, 199, 0), (255, 87, 34)),     # yellow -> orange
    ((100, 217, 255), (0, 91, 234)),    # sky -> deep blue
]


def _make_gradient_background(width, height):
    """Create a smooth diagonal gradient background."""
    top_color, bottom_color = random.choice(GRADIENTS)
    base = Image.new("RGB", (width, height), top_color)
    draw = ImageDraw.Draw(base)

    for y in range(height):
        ratio = y / height
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    return base


def _fit_text(draw, text, font_path, max_width, max_height, start_size=70, min_size=28):
    """Find the largest font size where wrapped text fits within max_width/max_height."""
    size = start_size
    while size >= min_size:
        font = ImageFont.truetype(font_path, size)
        # Estimate wrap width based on average character width
        avg_char_w = font.getbbox("A")[2] - font.getbbox("A")[0]
        wrap_chars = max(10, int(max_width / (avg_char_w * 0.62)))
        wrapped = textwrap.fill(text, width=wrap_chars)

        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=10)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        if text_w <= max_width and text_h <= max_height:
            return font, wrapped, text_w, text_h
        size -= 4

    font = ImageFont.truetype(font_path, min_size)
    wrapped = textwrap.fill(text, width=30)
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=10)
    return font, wrapped, bbox[2] - bbox[0], bbox[3] - bbox[1]


def _draw_outlined_text(draw, xy, text, font, fill, outline, outline_width=4, spacing=10):
    x, y = xy
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx * dx + dy * dy <= outline_width * outline_width:
                draw.multiline_text((x + dx, y + dy), text, font=font, fill=outline,
                                     align="center", spacing=spacing)
    draw.multiline_text((x, y), text, font=font, fill=fill, align="center", spacing=spacing)


def render_joke_image(setup: str, punchline: str = None) -> BytesIO:
    """
    Renders a joke onto a generated gradient background.
    If punchline is provided, setup is shown smaller near the top and punchline large in the center.
    If not, the whole joke text is centered.
    """
    img = _make_gradient_background(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)

    padding = 80
    max_width = WIDTH - padding * 2

    if punchline:
        # Setup text (smaller, upper area)
        setup_font, setup_wrapped, sw, sh = _fit_text(
            draw, setup, FONT_PATH, max_width, HEIGHT * 0.35, start_size=48, min_size=24
        )
        setup_x = (WIDTH - sw) / 2
        setup_y = HEIGHT * 0.12
        _draw_outlined_text(draw, (setup_x, setup_y), setup_wrapped, setup_font,
                             fill=(255, 255, 255), outline=(0, 0, 0), outline_width=3)

        # Punchline text (larger, centered lower)
        punch_font, punch_wrapped, pw, ph = _fit_text(
            draw, punchline, FONT_PATH, max_width, HEIGHT * 0.35, start_size=80, min_size=32
        )
        punch_x = (WIDTH - pw) / 2
        punch_y = HEIGHT * 0.55
        _draw_outlined_text(draw, (punch_x, punch_y), punch_wrapped, punch_font,
                             fill=(255, 240, 0), outline=(0, 0, 0), outline_width=5)
    else:
        font, wrapped, tw, th = _fit_text(
            draw, setup, FONT_PATH, max_width, HEIGHT * 0.7, start_size=70, min_size=28
        )
        x = (WIDTH - tw) / 2
        y = (HEIGHT - th) / 2
        _draw_outlined_text(draw, (x, y), wrapped, font,
                             fill=(255, 255, 255), outline=(0, 0, 0), outline_width=4)

    # Small watermark
    wm_font = ImageFont.truetype(FONT_PATH, 22)
    draw.text((WIDTH - 220, HEIGHT - 45), "😂 Meme Hub Bot", font=wm_font, fill=(255, 255, 255, 180))

    buf = BytesIO()
    buf.name = "joke.png"
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
