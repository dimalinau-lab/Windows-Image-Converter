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
    script_path = os.path.join(parent_dir, "main.py")

    python_exe = sys.executable
    pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")

    try:
        key_main = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"SystemFileAssociations\image\shell\MyPyConverter")
        winreg.SetValueEx(key_main, "MUIVerb", 0, winreg.REG_SZ, "Converter")
        winreg.SetValueEx(key_main, "ExtendedSubCommandsKey", 0, winreg.REG_SZ, "MyPyConverter")
        winreg.CloseKey(key_main)

        formats = [
            ("cmd1", "PNG", "png"),
            ("cmd2", "JPEG", "jpeg"),
            ("cmd3", "ICO", "ico"),
            ("cmd4", "WEBP", "webp"),
            ("cmd5", "BMP", "bmp"),
            ("cmd6", "GIF", "gif"),
            ("cmd7", "TIFF", "tiff")
        ]

        for cmd, name, ext in formats:
            key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, rf"MyPyConverter\shell\{cmd}")
            winreg.SetValue(key, "", winreg.REG_SZ, f"В формат {name}")
            key_cmd = winreg.CreateKey(key, "command")
            winreg.SetValue(key_cmd, "", winreg.REG_SZ, f'"{pythonw_exe}" "{script_path}" "%1" {ext}')
            winreg.CloseKey(key_cmd)
            winreg.CloseKey(key)

        ctypes.windll.user32.MessageBoxW(0, "Новые форматы успешно добавлены в меню Windows!", "Обновление завершено",
                                         0x40)
    except Exception as e:
        ctypes.windll.user32.MessageBoxW(0, f"Ошибка при записи в реестр: {e}", "Ошибка", 0x10)


if __name__ == "__main__":
    if is_admin():
        install()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{__file__}"', None, 1)