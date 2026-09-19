import winreg
import sys
import os
import ctypes
import traceback


def show_msg(title, text):
    ctypes.windll.user32.MessageBoxW(0, str(text), str(title), 0x40)


def show_err(text):
    ctypes.windll.user32.MessageBoxW(0, str(text), "Ошибка установки", 0x10)


def get_base_cmd():
    """Формирует точную команду запуска в зависимости от режима (exe или py)."""
    if getattr(sys, 'frozen', False):
        return f'"{sys.executable}"'

    pythonw_exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(pythonw_exe):
        pythonw_exe = sys.executable

    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.abspath(os.path.join(current_dir, "..", "main.py"))
    if not os.path.exists(main_script):
        main_script = os.path.abspath(sys.argv[0])

    return f'"{pythonw_exe}" "{main_script}"'


def needs_install():
    """
    Проверяет, нужно ли прописывать/обновлять реестр:
    1. Существует ли пункт в реестре.
    2. Совпадает ли путь запуска.
    3. Соответствует ли название новому ('Converter' вместо старого).
    """
    base_cmd = get_base_cmd()
    expected_sample_cmd = f'{base_cmd} "%1" png'
    root_key = winreg.HKEY_CURRENT_USER

    try:
        # Проверяем название главного пункта
        key = winreg.OpenKey(root_key, r"Software\Classes\SystemFileAssociations\image\shell\PyWIC")
        verb, _ = winreg.QueryValueEx(key, "MUIVerb")
        winreg.CloseKey(key)
        if verb != "Converter":
            return True

        # Проверяем команду запуска первого действия
        cmd_key = winreg.OpenKey(root_key, r"Software\Classes\PyWIC\shell\cmd1\command")
        cmd_val = winreg.QueryValue(cmd_key, "")  # Исправлено: QueryValue возвращает только строку
        winreg.CloseKey(cmd_key)
        if cmd_val != expected_sample_cmd:
            return True

        return False
    except (FileNotFoundError, OSError):
        return True


def install(silent=False):
    try:
        base_cmd = get_base_cmd()
        root_key = winreg.HKEY_CURRENT_USER
        base_path = r"Software\Classes"

        # Главный пункт для картинок
        img_path = rf"{base_path}\SystemFileAssociations\image\shell\PyWIC"
        key_main = winreg.CreateKey(root_key, img_path)
        winreg.SetValueEx(key_main, "MUIVerb", 0, winreg.REG_SZ, "Converter")
        winreg.SetValueEx(key_main, "ExtendedSubCommandsKey", 0, winreg.REG_SZ, r"PyWIC")
        winreg.CloseKey(key_main)

        # Подпункты
        cmds_path = rf"{base_path}\PyWIC\shell"
        formats = [
            ("cmd1", "В формат PNG", "png"),
            ("cmd2", "В формат JPEG", "jpeg"),
            ("cmd3", "В формат ICO", "ico"),
            ("cmd4", "В формат WEBP", "webp"),
            ("cmd5", "В формат BMP", "bmp"),
            ("cmd6", "Удалить фон (AI)", "remove_bg")
        ]
        for cmd, name, ext in formats:
            cmd_key_path = rf"{cmds_path}\{cmd}"
            key = winreg.CreateKey(root_key, cmd_key_path)
            winreg.SetValue(key, "", winreg.REG_SZ, name)

            key_cmd = winreg.CreateKey(key, "command")
            winreg.SetValue(key_cmd, "", winreg.REG_SZ, f'{base_cmd} "%1" {ext}')
            winreg.CloseKey(key_cmd)
            winreg.CloseKey(key)

        # PDF пункт
        pdf_path = rf"{base_path}\SystemFileAssociations\.pdf\shell\PyWICPdf"
        pdf_main = winreg.CreateKey(root_key, pdf_path)
        winreg.SetValue(pdf_main, "", winreg.REG_SZ, "Конвертировать в DOCX")
        pdf_cmd = winreg.CreateKey(pdf_main, "command")
        winreg.SetValue(pdf_cmd, "", winreg.REG_SZ, f'{base_cmd} "%1" docx')
        winreg.CloseKey(pdf_cmd)
        winreg.CloseKey(pdf_main)

        # DOCX пункт
        doc_path = rf"{base_path}\SystemFileAssociations\.docx\shell\PyWICDoc"
        doc_main = winreg.CreateKey(root_key, doc_path)
        winreg.SetValue(doc_main, "", winreg.REG_SZ, "Конвертировать в PDF")
        doc_cmd = winreg.CreateKey(doc_main, "command")
        winreg.SetValue(doc_cmd, "", winreg.REG_SZ, f'{base_cmd} "%1" pdf')
        winreg.CloseKey(doc_cmd)
        winreg.CloseKey(doc_main)

        if not silent:
            show_msg("Установка завершена", "Контекстное меню успешно настроено!")
    except Exception as e:
        if not silent:
            show_err(f"Сбой записи в реестр:\n{e}\n\n{traceback.format_exc()}")