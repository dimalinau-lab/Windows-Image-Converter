import sys
import os
import winreg
import subprocess
import pystray
from PIL import Image
from app.converter import convert_image

def is_installed():
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"SystemFileAssociations\image\shell\MyPyConverter")
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False

def is_autostart_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, "MyPyConverter")
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False

def toggle_autostart(icon, item):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        if is_autostart_enabled():
            winreg.DeleteValue(key, "MyPyConverter")
        else:
            if getattr(sys, 'frozen', False):
                cmd = f'"{sys.executable}"'
            else:
                pythonw_exe = sys.executable.replace("python.exe", "pythonw.exe")
                script_path = os.path.abspath(__file__)
                cmd = f'"{pythonw_exe}" "{script_path}"'
            winreg.SetValueEx(key, "MyPyConverter", 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Ошибка автозагрузки: {e}")

def exit_action(icon, item):
    icon.stop()

def start_tray():
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            current_dir = sys._MEIPASS
        else:
            current_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(current_dir, "assets", "icon.png")

    if os.path.exists(icon_path):
        image = Image.open(icon_path)
    else:
        image = Image.new('RGB', (64, 64), color='blue')

    menu = pystray.Menu(
        pystray.MenuItem("Автозагрузка", toggle_autostart, checked=lambda item: is_autostart_enabled()),
        pystray.MenuItem("Выход", exit_action)
    )

    tray_icon = pystray.Icon("PyConverter", image, "Converter", menu)
    tray_icon.run()

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        input_file = sys.argv[1]
        target_format = sys.argv[2]
        convert_image(input_file, target_format)
    elif len(sys.argv) == 1:
        if not is_installed():
            if getattr(sys, 'frozen', False):
                current_dir = os.path.dirname(sys.executable)
                python_exe = "python"
            else:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                python_exe = sys.executable

            installer_path = os.path.join(current_dir, "app", "installer.py")
            if os.path.exists(installer_path):
                subprocess.run([python_exe, installer_path])

        start_tray()
    else:
        sys.exit()