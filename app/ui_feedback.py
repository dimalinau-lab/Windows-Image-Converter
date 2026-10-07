import threading
import os
import sys

def run_with_progress(title, text, task_func):
    """
    Отображает ненавязчивое всплывающее окно прогресса в правом нижнем углу экрана,
    пока task_func выполняется в отдельном рабочем потоке.
    """
    try:
        import tkinter as tk
        from tkinter import ttk
    except Exception:
        # Если Tkinter недоступен, выполняем напрямую без окна
        return task_func()

    root = None
    try:
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes('-topmost', True)
        root.configure(bg='#202020')

        # Размеры окна и позиционирование в правом нижнем углу над панелью задач
        width, height = 330, 80
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        pos_x = screen_w - width - 20
        pos_y = screen_h - height - 60
        root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

        # Рамка карточки
        card = tk.Frame(root, bg='#2b2b2b', highlightbackground='#4a4a4a', highlightthickness=1)
        card.pack(fill='both', expand=True, padx=1, pady=1)

        # Заголовок
        lbl_title = tk.Label(
            card,
            text=title,
            font=('Segoe UI', 10, 'bold'),
            fg='#ffffff',
            bg='#2b2b2b'
        )
        lbl_title.pack(anchor='w', padx=12, pady=(8, 2))

        # Описание (имя файла или статус)
        lbl_text = tk.Label(
            card,
            text=text,
            font=('Segoe UI', 9),
            fg='#b5b5b5',
            bg='#2b2b2b'
        )
        lbl_text.pack(anchor='w', padx=12, pady=(0, 6))

        # Стиль прогресс-бара
        style = ttk.Style(root)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure(
            'Modern.Horizontal.TProgressbar',
            background='#0078d4',
            troughcolor='#383838',
            bordercolor='#2b2b2b',
            lightcolor='#0078d4',
            darkcolor='#0078d4'
        )

        pb = ttk.Progressbar(card, mode='indeterminate', style='Modern.Horizontal.TProgressbar')
        pb.pack(fill='x', padx=12, pady=(0, 8))
        pb.start(10)

        result = {'error': None, 'output': None}

        def worker():
            try:
                result['output'] = task_func()
            except Exception as e:
                result['error'] = e
            finally:
                def close_window():
                    try:
                        root.quit()
                    except Exception:
                        pass
                    try:
                        root.destroy()
                    except Exception:
                        pass
                try:
                    root.after(0, close_window)
                except Exception:
                    pass

        t = threading.Thread(target=worker, daemon=True)
        t.start()

        root.mainloop()

        if result['error'] is not None:
            raise result['error']
        return result['output']

    except Exception as e:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
        # Если была ошибка внутри task_func, пробрасываем её
        if 'result' in locals() and result.get('error') is not None:
            raise result['error']
        # Если ошибка самого Tkinter, запускаем задачу напрямую
        return task_func()
