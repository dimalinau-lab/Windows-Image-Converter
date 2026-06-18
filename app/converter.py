import os
import ctypes
from PIL import Image


def show_error(message):
    ctypes.windll.user32.MessageBoxW(0, str(message), "Ошибка конвертации", 0x10)


def convert_image(input_path, target_format):
    try:
        img = Image.open(input_path)
        base_name = os.path.splitext(input_path)[0]
        fmt = target_format.lower()
        output_path = f"{base_name}.{fmt}"

        no_alpha_formats = ['jpg', 'jpeg', 'bmp']

        if fmt in no_alpha_formats and img.mode in ('RGBA', 'P', 'LA'):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
            img = background

        if fmt == 'ico':
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            img = img.resize((256, 256), Image.Resampling.LANCZOS)
            img.save(output_path, format='ICO', sizes=[(256, 256)])
        else:
            img.save(output_path)

    except Exception as e:
        show_error(f"Не удалось конвертировать файл:\n{e}")