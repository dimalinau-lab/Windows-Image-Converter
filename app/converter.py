import os
import sys

class DummyStream:
    def write(self, *args, **kwargs): pass
    def flush(self, *args, **kwargs): pass
    def isatty(self): return False

if sys.stdout is None:
    sys.stdout = DummyStream()
if sys.stderr is None:
    sys.stderr = DummyStream()

from PIL import Image

try:
    from pdf2docx import Converter
    from docx2pdf import convert as convert_docx_to_pdf
    DOCS_READY = True
except ImportError:
    DOCS_READY = False

try:
    from rembg import remove
    REMBG_READY = True
except ImportError:
    REMBG_READY = False

def convert_image(input_file, target_format):
    ext = input_file.split('.')[-1].lower()
    target_format = target_format.lower()

    if target_format == 'remove_bg':
        if REMBG_READY:
            try:
                img = Image.open(input_file)
                output_img = remove(img)
                out_file = input_file.rsplit('.', 1)[0] + '_nobg.png'
                output_img.save(out_file, format='PNG')
            except Exception:
                pass
        return

    if ext in ['pdf', 'doc', 'docx']:
        if DOCS_READY:
            try:
                if ext == 'pdf' and target_format == 'docx':
                    out_file = input_file.rsplit('.', 1)[0] + '.docx'
                    cv = Converter(input_file)
                    cv.convert(out_file, start=0, end=None)
                    cv.close()

                elif ext in ['doc', 'docx'] and target_format == 'pdf':
                    out_file = input_file.rsplit('.', 1)[0] + '.pdf'
                    convert_docx_to_pdf(input_file, out_file)
            except Exception:
                pass
        return

    try:
        img = Image.open(input_file)
        out_file = input_file.rsplit('.', 1)[0] + '.' + target_format

        if target_format in ['jpeg', 'jpg', 'bmp']:
            if img.mode in ('RGBA', 'LA', 'P'):
                bg = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                bg.paste(img, mask=img.split()[3])
                img = bg
        elif target_format == 'ico':
            img = img.resize((256, 256))

        save_format = target_format.upper()
        if save_format == 'JPG':
            save_format = 'JPEG'

        img.save(out_file, format=save_format)
    except Exception:
        pass