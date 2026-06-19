import winreg
import sys
import os
import ctypes
import traceback


def show_msg(title, text):
    ctypes.windll.user32.MessageBoxW(0, str(text), str(title), 0x40)


def show_err(text):
    ctypes.windll.user32.MessageBoxW(0, str(text), "Ошибка установки", 0x10)


def install():
    try:
        # Переключаемся на pythonw.exe, чтобы полностью скрыть консоль
        if getattr(sys, 'frozen', False):
            base_cmd = f'"{sys.executable}"'
        else:
            pythonw_exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            if not os.path.exists(pythonw_exe):
                pythonw_exe = sys.executable
            main_script = os.path.abspath(sys.argv[0])
            base_cmd = f'"{pythonw_exe}" "{main_script}"'

        root_key = winreg.HKEY_CURRENT_USER
        base_path = r"Software\Classes"

        # Меню для картинок
        img_path = rf"{base_path}\SystemFileAssociations\image\shell\PyWIC"
        key_main = winreg.CreateKey(root_key, img_path)
        winreg.SetValueEx(key_main, "MUIVerb", 0, winreg.REG_SZ, "🔮 Python Converter")
        winreg.SetValueEx(key_main, "ExtendedSubCommandsKey", 0, winreg.REG_SZ, r"PyWIC")
        winreg.CloseKey(key_main)

        cmds_path = rf"{base_path}\PyWIC\shell"
        formats = [
            ("cmd1", "В формат PNG", "png"), ("cmd2", "В формат JPEG", "jpeg"),
            ("cmd3", "В формат ICO", "ico"), ("cmd4", "В формат WEBP", "webp"),
            ("cmd5", "В формат BMP", "bmp"), ("cmd6", "✨ Удалить фон (AI)", "remove_bg")
        ]
        for cmd, name, ext in formats:
            cmd_key_path = rf"{cmds_path}\{cmd}"
            key = winreg.CreateKey(root_key, cmd_key_path)
            winreg.SetValue(key, "", winreg.REG_SZ, name)

            key_cmd = winreg.CreateKey(key, "command")
            winreg.SetValue(key_cmd, "", winreg.REG_SZ, f'{base_cmd} "%1" {ext}')
            winreg.CloseKey(key_cmd)
            winreg.CloseKey(key)

        # PDF
        pdf_path = rf"{base_path}\SystemFileAssociations\.pdf\shell\PyWICPdf"
        pdf_main = winreg.CreateKey(root_key, pdf_path)
        winreg.SetValue(pdf_main, "", winreg.REG_SZ, "🔮 Конвертировать в DOCX")
        pdf_cmd = winreg.CreateKey(pdf_main, "command")
        winreg.SetValue(pdf_cmd, "", winreg.REG_SZ, f'{base_cmd} "%1" docx')
        winreg.CloseKey(pdf_cmd)
        winreg.CloseKey(pdf_main)

        # DOCX
        doc_path = rf"{base_path}\SystemFileAssociations\.docx\shell\PyWICDoc"
        doc_main = winreg.CreateKey(root_key, doc_path)
        winreg.SetValue(doc_main, "", winreg.REG_SZ, "🔮 Конвертировать в PDF")
        doc_cmd = winreg.CreateKey(doc_main, "command")
        winreg.SetValue(doc_cmd, "", winreg.REG_SZ, f'{base_cmd} "%1" pdf')
        winreg.CloseKey(doc_cmd)
        winreg.CloseKey(doc_main)

        show_msg("Установка завершена", "Меню успешно добавлено (Бесшумный режим)!")
    except Exception as e:
        show_err(f"Сбой записи:\n{e}\n\n{traceback.format_exc()}")