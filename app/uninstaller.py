import winreg
import ctypes


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
    root = winreg.HKEY_CURRENT_USER

    # 1. Удаляем контекстные меню
    keys_to_remove = [
        r"Software\Classes\SystemFileAssociations\image\shell\PyWIC",
        r"Software\Classes\PyWIC",
        r"Software\Classes\SystemFileAssociations\.pdf\shell\PyWICPdf",
        r"Software\Classes\SystemFileAssociations\.docx\shell\PyWICDoc"
    ]
    for path in keys_to_remove:
        delete_registry_tree(root, path)

    # 2. Удаляем из автозагрузки, если была включена
    try:
        key = winreg.OpenKey(root, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "PyWICConverter")
        winreg.CloseKey(key)
    except OSError:
        pass

    ctypes.windll.user32.MessageBoxW(0, "Пункты Converter успешно удалены из Windows!", "Удаление завершено", 0x40)


if __name__ == "__main__":
    uninstall()