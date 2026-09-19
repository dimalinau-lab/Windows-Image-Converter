import sys
import os
import winreg
import ctypes
import multiprocessing
import traceback

def show_error(msg):
    ctypes.windll.user32.MessageBoxW(0, str(msg), "Ошибка программы", 0x10)

def ask_confirm(text, title="Подтверждение"):
    # 0x24: MB_YESNO | MB_ICONQUESTION, 6 = IDYES
    return ctypes.windll.user32.MessageBoxW(0, str(text), str(title), 0x24) == 6

try:
    import pystray
    from PIL import Image
    from app.converter import convert_image
    from app.installer import install, needs_install
    from app.uninstaller import uninstall
except Exception:
    show_error(traceback.format_exc())
    sys.exit(1)

REG_APP_PATH = r"Software\Classes\PyWIC"

def is_first_run():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_APP_PATH, 0, winreg.KEY_READ)
        val, _ = winreg.QueryValueEx(key, "FirstRunCompleted")
        winreg.CloseKey(key)
        return val != 1
    except (FileNotFoundError, OSError):
        return True

def mark_first_run_done():
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_APP_PATH)
        winreg.SetValueEx(key, "FirstRunCompleted", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
    except Exception:
        pass

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
        install(silent=False)
    except Exception:
        show_error(traceback.format_exc())

def manual_uninstall(icon, item):
    if ask_confirm("Вы действительно хотите удалить пункты конвертера из контекстного меню Windows?"):
        try:
            uninstall()
        except Exception:
            show_error(traceback.format_exc())

def exit_action(icon, item):
    icon.stop()
    sys.exit(0)

def on_tray_ready(icon):
    icon.visible = True
    if is_first_run():
        icon.notify(
            "Приложение свернуто в трей.\nКликните правой кнопкой мыши для настройки автозагрузки или удаления меню.",
            "Converter запущен"
        )
        mark_first_run_done()

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
            pystray.MenuItem("Обновить меню", manual_install),
            pystray.MenuItem("Автозагрузка", toggle_autostart, checked=lambda item: is_autostart_enabled()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Удалить из проводника", manual_uninstall),
            pystray.MenuItem("Выход", exit_action)
        )

        tray_icon = pystray.Icon("WIC", image, "Converter", menu)
        tray_icon.run(setup=on_tray_ready)
    except Exception:
        show_error("Ошибка в трее:\n" + traceback.format_exc())

def main():
    try:
        if len(sys.argv) >= 3:
            convert_image(sys.argv[1], sys.argv[2])
            sys.exit(0)

        if len(sys.argv) == 2:
            if sys.argv[1] == "--install":
                install(silent=True)
                sys.exit(0)
            elif sys.argv[1] == "--uninstall":
                uninstall()
                sys.exit(0)

        if needs_install():
            install(silent=True)

        start_tray()
    except Exception:
        show_error("Ошибка в main:\n" + traceback.format_exc())

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()