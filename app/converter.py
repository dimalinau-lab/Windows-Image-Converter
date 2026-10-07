import os
import sys
import json
import ctypes
import traceback

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
from app.ui_feedback import run_with_progress


def load_config():
    try:
        if getattr(sys, 'frozen', False):
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "data", "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"notifications": True, "default_quality": 95}


def show_msg(text, title, style=0x40):
    ctypes.windll.user32.MessageBoxW(0, str(text), str(title), style)


def show_success(text, title="Готово"):
    config = load_config()
    if config.get("notifications", True):
        show_msg(text, title, 0x40)


def check_and_notify_ai():
    model_path = os.path.expanduser("~/.u2net/u2net.onnx")
    if not os.path.exists(model_path):
        show_msg("Сейчас программа скачает ИИ-модель (170 МБ).\nПожалуйста, подождите около минуты.", "Загрузка ИИ", 0x40)


def find_libreoffice():
    paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    import shutil
    return shutil.which("soffice")


def convert_word_to_pdf(input_file, out_file):
    abs_input = os.path.abspath(input_file)
    abs_output = os.path.abspath(out_file)

    com_err_msg = None
    # 1. Попытка через Microsoft Word COM API (поддерживает .doc и .docx)
    try:
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()
        word = None
        doc = None
        try:
            word = win32com.client.DispatchEx("Word.Application")
            word.Visible = False
            word.DisplayAlerts = 0  # wdAlertsNone - подавляет всплывающие диалоги

            # Ключевая оптимизация скорости: переключаем виртуальный принтер на локальный
            # для устранения 45-секундного сетевого таймаута при экспорте в PDF
            try:
                word.ActivePrinter = "Microsoft Print to PDF"
            except Exception:
                pass

            try:
                word.ScreenUpdating = False
            except Exception:
                pass

            # Открываем документ с отключением лишних фоновых операций
            doc = word.Documents.Open(
                abs_input,
                ReadOnly=True,
                ConfirmConversions=False,
                AddToRecentFiles=False,
                Visible=False
            )

            # Сохраняем в формат PDF
            doc.SaveAs(abs_output, FileFormat=17)
            return
        finally:
            if doc is not None:
                try:
                    doc.Close(0)  # wdDoNotSaveChanges
                except Exception:
                    pass
            if word is not None:
                try:
                    word.NormalTemplate.Saved = True
                    word.Quit(0)  # wdDoNotSaveChanges
                except Exception:
                    pass
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
    except Exception as e:
        com_err_msg = str(e)

    # 2. Фоллбек: попытка через LibreOffice, если установлен
    libreoffice = find_libreoffice()
    if libreoffice:
        try:
            import subprocess
            out_dir = os.path.dirname(abs_output)
            cmd = [libreoffice, "--headless", "--convert-to", "pdf", abs_input, "--outdir", out_dir]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            if res.returncode == 0 and os.path.exists(abs_output):
                return
        except Exception:
            pass

    # 3. Если ни один способ не сработал
    detail = f"\nОшибка Word COM: {com_err_msg}" if com_err_msg else ""
    raise RuntimeError(
        f"Не удалось конвертировать документ Word в PDF.{detail}\n\n"
        f"Убедитесь, что Microsoft Word установлен и активирован."
    )


def convert_pdf_to_docx(input_file, out_file):
    from pdf2docx import Converter
    cv = Converter(input_file)
    try:
        # Многопроцессорное ускорение для многостраничных документов
        page_count = len(cv._fitz_doc)
        if page_count > 2:
            cv.convert(out_file, start=0, end=None, multi_processing=True, cpu_count=0)
        else:
            cv.convert(out_file, start=0, end=None)
    finally:
        cv.close()


def convert_image(input_file, target_format):
    ext = input_file.rsplit('.', 1)[-1].lower() if '.' in input_file else ''
    target_format = target_format.lower()
    base_name = os.path.basename(input_file)
    config = load_config()
    quality = config.get("default_quality", 95)

    # --- 1. ЛОГИКА ДЛЯ ИИ (УДАЛЕНИЕ ФОНА) ---
    if target_format == 'remove_bg':
        try:
            check_and_notify_ai()
            out_file = input_file.rsplit('.', 1)[0] + '_nobg.png'

            def do_remove_bg():
                from rembg import remove
                img = Image.open(input_file)
                output_img = remove(img)
                output_img.save(out_file, format='PNG')

            run_with_progress("Удаление фона (AI)", f"Обработка: {base_name}", do_remove_bg)
            show_success("Фон успешно удален!")
        except Exception as e:
            show_msg(f"Системный сбой ИИ:\n{e}", "Критическая ошибка", 0x10)
        return

    # --- 2. ЛОГИКА ДЛЯ ДОКУМЕНТОВ ---
    if ext in ['pdf', 'doc', 'docx']:
        try:
            if ext == 'pdf' and target_format == 'docx':
                out_file = input_file.rsplit('.', 1)[0] + '.docx'

                def do_pdf_to_docx():
                    convert_pdf_to_docx(input_file, out_file)

                run_with_progress("Конвертация PDF в DOCX", f"Обработка: {base_name}", do_pdf_to_docx)
                show_success("Документ успешно конвертирован в DOCX!")

            elif ext in ['doc', 'docx'] and target_format == 'pdf':
                out_file = input_file.rsplit('.', 1)[0] + '.pdf'

                def do_doc_to_pdf():
                    convert_word_to_pdf(input_file, out_file)

                run_with_progress("Конвертация в PDF", f"Обработка: {base_name}", do_doc_to_pdf)
                show_success("Документ успешно конвертирован в PDF!")
        except Exception as e:
            show_msg(f"Ошибка конвертации документа:\n{e}", "Ошибка", 0x10)
        return

    # --- 3. ЛОГИКА ДЛЯ ИЗОБРАЖЕНИЙ ---
    try:
        out_file = input_file.rsplit('.', 1)[0] + '.' + target_format

        def do_convert_image():
            img = Image.open(input_file)

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
                return

            save_format = target_format.upper()
            if save_format == 'JPG':
                save_format = 'JPEG'

            save_kwargs = {"format": save_format}
            if save_format in ('JPEG', 'WEBP'):
                save_kwargs["quality"] = quality

            img.save(out_file, **save_kwargs)

        run_with_progress("Конвертация изображения", f"Преобразование в {target_format.upper()}...", do_convert_image)
        show_success("Картинка успешно конвертирована!")
    except Exception as e:
        show_msg(f"Ошибка конвертации: {e}", "Ошибка", 0x10)