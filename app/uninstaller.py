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

    # 1. Удаляем контекстные меню (текущие и старые версии)
    keys_to_remove = [
        # Текущая версия (PyWIC)
        r"Software\Classes\SystemFileAssociations\image\shell\PyWIC",
        r"Software\Classes\PyWIC",
        r"Software\Classes\SystemFileAssociations\.pdf\shell\PyWICPdf",
        r"Software\Classes\SystemFileAssociations\.docx\shell\PyWICDoc",
        r"Software\Classes\SystemFileAssociations\.doc\shell\PyWICDoc",

        # Старые версии (MyPyConverter, MyDocConverter, MyPdfConverter, ConvertToPdf, ConvertToDocx)
        r"Software\Classes\SystemFileAssociations\.docx\shell\ConvertToPdf",
        r"Software\Classes\SystemFileAssociations\.doc\shell\ConvertToPdf",
        r"Software\Classes\SystemFileAssociations\.pdf\shell\ConvertToDocx",
        r"Software\Classes\SystemFileAssociations\.docx\shell\MyDocConverter",
        r"Software\Classes\SystemFileAssociations\.doc\shell\MyDocConverter",
        r"Software\Classes\SystemFileAssociations\.pdf\shell\MyPdfConverter",
        r"Software\Classes\SystemFileAssociations\image\shell\MyPyConverter",
        r"Software\Classes\MyDocConverter",
        r"Software\Classes\MyPdfConverter",
        r"Software\Classes\MyPyConverter"
    ]

    # Очистка в HKCU
    for path in keys_to_remove:
        delete_registry_tree(winreg.HKEY_CURRENT_USER, path)

    # Очистка в HKLM (если есть права администратора)
    for path in keys_to_remove:
        delete_registry_tree(winreg.HKEY_LOCAL_MACHINE, path)

    # 2. Удаляем из автозагрузки, если была включена
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "PyWICConverter")
        winreg.CloseKey(key)
    except OSError:
        pass

    ctypes.windll.user32.MessageBoxW(0, "Пункты Converter успешно удалены из Windows!", "Удаление завершено", 0x40)


if __name__ == "__main__":
    uninstall()