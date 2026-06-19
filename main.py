import sys
import os
import winreg
import ctypes
import multiprocessing
import traceback

def show_error(msg):
    ctypes.windll.user32.MessageBoxW(0, str(msg), "Ошибка программы", 0x10)

try:
    import pystray
    from PIL import Image
    from app.converter import convert_image
    from app.installer import install
except Exception:
    show_error(traceback.format_exc())
    sys.exit()

def is_installed():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\SystemFileAssociations\image\shell\PyWIC")
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False

def is_autostart_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, "PyWICConverter")
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False

def toggle_autostart(icon, item):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        if is_autostart_enabled():
            winreg.DeleteValue(key, "PyWICConverter")
        else:
            if getattr(sys, 'frozen', False):
                cmd = f'"{sys.executable}"'
            else:
                pythonw_exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
                if not os.path.exists(pythonw_exe):
                    pythonw_exe = sys.executable
                cmd = f'"{pythonw_exe}" "{os.path.abspath(__file__)}"'
            winreg.SetValueEx(key, "PyWICConverter", 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
    except Exception:
        pass

def manual_install(icon, item):
    try:
        install()
    except Exception:
        show_error(traceback.format_exc())

def exit_action(icon, item):
    icon.stop()
    sys.exit(0)

def start_tray():
    try:
        if getattr(sys, 'frozen', False):
            current_dir = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))

        icon_path = os.path.join(current_dir, "assets", "icon.png")

        if os.path.exists(icon_path):
            image = Image.open(icon_path)
        else:
            image = Image.new('RGB', (64, 64), color='blue')

        menu = pystray.Menu(
            pystray.MenuItem("Установить меню", manual_install),
            pystray.MenuItem("Автозагрузка", toggle_autostart, checked=lambda item: is_autostart_enabled()),
            pystray.MenuItem("Выход", exit_action)
        )

        tray_icon = pystray.Icon("WIC", image, "Python Converter", menu)
        tray_icon.run()
    except Exception:
        show_error("Ошибка в трее:\n" + traceback.format_exc())

def main():
    try:
        # --- БЛОК КОНВЕРТАЦИИ ---
        if len(sys.argv) >= 3:
            convert_image(sys.argv[1], sys.argv[2])
            sys.exit(0)

        # --- БЛОК УСТАНОВКИ МЕНЮ ---
        if len(sys.argv) == 2 and sys.argv[1] == "--install":
            try:
                install()
            except Exception:
                show_error("Ошибка установки реестра:\n" + traceback.format_exc())
            sys.exit(0)

        if not is_installed():
            install()

        start_tray()
    except Exception:
        show_error("Ошибка в main:\n" + traceback.format_exc())

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()