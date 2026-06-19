import winreg
import sys
import ctypes


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def delete_registry_tree(hkey, subkey):
    try:
        key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_ALL_ACCESS)
    except OSError:
        return
    while True:
        try:
            sub_name = winreg.EnumKey(key, 0)
            delete_registry_tree(hkey, subkey + "\\" + sub_name)
        except OSError:
            break

    winreg.CloseKey(key)

    try:
        winreg.DeleteKey(hkey, subkey)
    except OSError:
        pass


def uninstall():
    main_key_path = r"SystemFileAssociations\image\shell\MyPyConverter"

    try:
        delete_registry_tree(winreg.HKEY_CLASSES_ROOT, main_key_path)
        ctypes.windll.user32.MessageBoxW(0, "Конвертер успешно удален из контекстного меню Windows!",
                                         "Удаление завершено", 0x40)
    except Exception as e:
        ctypes.windll.user32.MessageBoxW(0, f"Ошибка при очистке реестра: {e}", "Ошибка", 0x10)


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()

    if is_admin():
        uninstall()
    else:
        import ctypes
        import sys
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{__file__}"', None, 1)