from PIL import Image, ImageDraw
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / 'static' / 'img'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# prefer rasterizing the existing SVG asset if cairosvg is available
SVG_PATH = Path(__file__).resolve().parent.parent / 'static' / 'img' / 'favicon.svg'


def fallback_draw_gradient_background(draw, size, top_color=(43, 88, 118), bottom_color=(78, 67, 118)):
    for y in range(size):
        t = y / (size - 1)
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        draw.line([(0, y), (size, y)], fill=(r, g, b))


def fallback_draw_gamepad(draw, size):
    pad_w = int(size * 0.8)
    pad_h = int(size * 0.42)
    pad_x = (size - pad_w) // 2
    pad_y = int(size * 0.34)
    radius = int(size * 0.12)
    draw.rounded_rectangle([pad_x, pad_y, pad_x + pad_w, pad_y + pad_h], radius=radius, fill=(15, 23, 36))

    cx = pad_x + int(pad_w * 0.22)
    cy = pad_y + int(pad_h * 0.48)
    arm = int(size * 0.06)
    draw.rectangle([cx - arm // 2, cy - arm * 2, cx + arm // 2, cy + arm * 2], fill=(255, 255, 255))
    draw.rectangle([cx - arm * 2, cy - arm // 2, cx + arm * 2, cy + arm // 2], fill=(255, 255, 255))

    bx = pad_x + int(pad_w * 0.74)
    by = pad_y + int(pad_h * 0.38)
    spacing = int(size * 0.08)
    rbtn = int(size * 0.045)
    colors = [(255, 77, 109), (255, 217, 91), (62, 232, 166), (110, 161, 255)]
    offsets = [(-spacing, -spacing), (spacing, -spacing), (-spacing, spacing), (spacing, spacing)]
    for (ox, oy), col in zip(offsets, colors):
        draw.ellipse([bx + ox - rbtn, by + oy - rbtn, bx + ox + rbtn, by + oy + rbtn], fill=col)


def fallback_make_icon(size, out_path):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    fallback_draw_gradient_background(draw, size)
    margin = int(size * 0.06)
    draw.rounded_rectangle([margin, margin, size - margin, size - margin], radius=int(size * 0.1), fill=None, outline=(255, 255, 255, 40))
    fallback_draw_gamepad(draw, size)
    img.save(out_path, format='PNG')
    print('Wrote', out_path)


def make_icon(size, out_path):
    # Try to rasterize the SVG if possible
    try:
        import cairosvg
        if SVG_PATH.exists():
            cairosvg.svg2png(url=str(SVG_PATH), write_to=str(out_path), output_width=size, output_height=size)
            print('Wrote', out_path, '(from SVG)')
            return
    except Exception:
        # fall through to programmatic fallback
        pass

    # fallback drawing if svg rasterization not available
    fallback_make_icon(size, out_path)


if __name__ == '__main__':
    make_icon(192, OUT_DIR / 'icon-192.png')
    # Apple touch icon (recommended 180x180)
    make_icon(180, OUT_DIR / 'apple-touch-icon.png')
    make_icon(512, OUT_DIR / 'icon-512.png')
    # also create favicon.ico (multiple sizes) - prefer rasterizing SVG then saving as ICO
    try:
        import io
        from PIL import Image
        # try rasterizing a large PNG from SVG
        try:
            import cairosvg
            png_bytes = cairosvg.svg2png(url=str(SVG_PATH), output_width=512, output_height=512)
            img = Image.open(io.BytesIO(png_bytes)).convert('RGBA')
        except Exception:
            # fallback to programmatic render
            make_icon(512, OUT_DIR / 'temp-512.png')
            img = Image.open(OUT_DIR / 'temp-512.png').convert('RGBA')

        ico_path = OUT_DIR / 'favicon.ico'
        img.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])
        # remove temp file if used
        try:
            (OUT_DIR / 'temp-512.png').unlink()
        except Exception:
            pass
        print('Wrote', ico_path)
    except Exception as e:
        print('Could not write favicon.ico:', e)
