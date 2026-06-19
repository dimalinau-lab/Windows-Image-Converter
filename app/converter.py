import os
import sys
import ctypes


class DummyStream:
    def write(self, *args, **kwargs): pass

    def flush(self, *args, **kwargs): pass

    def isatty(self): return False

    def fileno(self): return 1


if sys.stdout is None:
    sys.stdout = DummyStream()
if sys.stderr is None:
    sys.stderr = DummyStream()

from PIL import Image


def show_msg(text, title, style=0x40):
    ctypes.windll.user32.MessageBoxW(0, str(text), str(title), style)


def check_and_notify_ai():
    model_path = os.path.expanduser("~/.u2net/u2net.onnx")
    if not os.path.exists(model_path):
        show_msg("Сейчас программа скачает ИИ-модель (170 МБ).\nПодождите около минуты.", "Загрузка ИИ", 0x40)


def convert_image(input_file, target_format):
    ext = input_file.split('.')[-1].lower()
    target_format = target_format.lower()

    # --- 1. ЛОГИКА ДЛЯ ИИ (УДАЛЕНИЕ ФОНА) ---
    if target_format == 'remove_bg':
        try:
            # Мгновенно выводим статус-окно для пользователя
            show_msg("Удаление фона запущено.\nПожалуйста, подождите, это займет около 20 секунд.", "WIC AI Processing")

            check_and_notify_ai()

            from rembg import remove
            img = Image.open(input_file)
            output_img = remove(img)
            out_file = input_file.rsplit('.', 1)[0] + '_nobg.png'
            output_img.save(out_file, format='PNG')
            show_msg("Фон успешно удален!", "Готово", 0x40)
        except Exception as e:
            show_msg(f"Системный сбой ИИ:\n{e}", "Критическая ошибка", 0x10)
        return

    # --- 2. ЛОГИКА ДЛЯ ДОКУМЕНТОВ ---
    if ext in ['pdf', 'doc', 'docx']:
        try:
            if ext == 'pdf' and target_format == 'docx':
                from pdf2docx import Converter
                out_file = input_file.rsplit('.', 1)[0] + '.docx'
                cv = Converter(input_file)
                cv.convert(out_file, start=0, end=None)
                cv.close()
            elif ext in ['doc', 'docx'] and target_format == 'pdf':
                from docx2pdf import convert as convert_docx_to_pdf
                out_file = input_file.rsplit('.', 1)[0] + '.pdf'
                convert_docx_to_pdf(input_file, out_file)
            show_msg("Документ успешно конвертирован!", "Готово", 0x40)
        except Exception as e:
            show_msg(f"Ошибка с документом:\n{e}", "Ошибка", 0x10)
        return

    # --- 3. ЛОГИКА ДЛЯ ОБЫЧНЫХ КАРТИНОК ---
    try:
        img = Image.open(input_file)
        out_file = input_file.rsplit('.', 1)[0] + '.' + target_format

        if target_format in ['jpeg', 'jpg', 'bmp']:
            if img.mode in ('RGBA', 'LA', 'P'):
                bg = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                try:
                    bg.paste(img, mask=img.split()[3])
                except IndexError:
                    bg.paste(img)
                img = bg

        elif target_format == 'ico':
            img = img.convert("RGBA")
            icon_sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
            img.save(out_file, format='ICO', sizes=icon_sizes)
            show_msg("Иконка успешно создана!", "Готово", 0x40)
            return

        save_format = target_format.upper()
        if save_format == 'JPG':
            save_format = 'JPEG'

        img.save(out_file, format=save_format)
        show_msg("Картинка успешно конвертирована!", "Готово", 0x40)
    except Exception as e:
        show_msg(f"Ошибка конвертации: {e}", "Ошибка", 0x10)