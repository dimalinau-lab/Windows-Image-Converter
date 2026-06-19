import winreg
import sys
import ctypes
import os


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def install():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)

    exe_path = os.path.join(parent_dir, "WIC.exe")
    script_path = os.path.join(parent_dir, "main.py")

    if os.path.exists(exe_path):
        base_cmd = f'"{exe_path}"'
    else:
        pythonw_exe = sys.executable.replace("python.exe", "pythonw.exe")
        base_cmd = f'"{pythonw_exe}" "{script_path}"'

    try:
        key_main = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"SystemFileAssociations\image\shell\MyPyConverter")
        winreg.SetValueEx(key_main, "MUIVerb", 0, winreg.REG_SZ, "Converter")
        winreg.SetValueEx(key_main, "ExtendedSubCommandsKey", 0, winreg.REG_SZ, "MyPyConverter")
        winreg.CloseKey(key_main)

        formats = [
            ("cmd1", "В формат PNG", "png"),
            ("cmd2", "В формат JPEG", "jpeg"),
            ("cmd3", "В формат ICO", "ico"),
            ("cmd4", "В формат WEBP", "webp"),
            ("cmd5", "В формат BMP", "bmp"),
            ("cmd6", "В формат GIF", "gif"),
            ("cmd7", "В формат TIFF", "tiff"),
            ("cmd8", "✨ Удалить фон (AI)", "remove_bg")
        ]

        for cmd, name, ext in formats:
            key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, rf"MyPyConverter\shell\{cmd}")
            winreg.SetValue(key, "", winreg.REG_SZ, name)
            key_cmd = winreg.CreateKey(key, "command")
            winreg.SetValue(key_cmd, "", winreg.REG_SZ, f'{base_cmd} "%1" {ext}')
            winreg.CloseKey(key_cmd)
            winreg.CloseKey(key)

        pdf_main = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"SystemFileAssociations\.pdf\shell\MyPdfConverter")
        winreg.SetValueEx(pdf_main, "MUIVerb", 0, winreg.REG_SZ, "🔮 Converter")
        winreg.SetValueEx(pdf_main, "ExtendedSubCommandsKey", 0, winreg.REG_SZ, "MyPdfConverter")
        winreg.CloseKey(pdf_main)

        pdf_sub = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"MyPdfConverter\shell\cmd1")
        winreg.SetValue(pdf_sub, "", winreg.REG_SZ, "В формат DOCX")
        pdf_cmd = winreg.CreateKey(pdf_sub, "command")
        winreg.SetValue(pdf_cmd, "", winreg.REG_SZ, f'{base_cmd} "%1" docx')
        winreg.CloseKey(pdf_cmd)
        winreg.CloseKey(pdf_sub)

        for doc_ext in [r"\.docx", r"\.doc"]:
            doc_main = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT,
                                        rf"SystemFileAssociations{doc_ext}\shell\MyDocConverter")
            winreg.SetValueEx(doc_main, "MUIVerb", 0, winreg.REG_SZ, "🔮 Converter")
            winreg.SetValueEx(doc_main, "ExtendedSubCommandsKey", 0, winreg.REG_SZ, "MyDocConverter")
            winreg.CloseKey(doc_main)

            doc_sub = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"MyDocConverter\shell\cmd1")
            winreg.SetValue(doc_sub, "", winreg.REG_SZ, "В формат PDF")
            doc_cmd = winreg.CreateKey(doc_sub, "command")
            winreg.SetValue(doc_cmd, "", winreg.REG_SZ, f'{base_cmd} "%1" pdf')
            winreg.CloseKey(doc_cmd)
            winreg.CloseKey(doc_sub)

        ctypes.windll.user32.MessageBoxW(0, "успешно обновлено!", "Готово", 0x40)
    except Exception as e:
        ctypes.windll.user32.MessageBoxW(0, f"Ошибка: {e}", "Ошибка", 0x10)


if __name__ == "__main__":
    if is_admin():
        install()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{__file__}"', None, 1)