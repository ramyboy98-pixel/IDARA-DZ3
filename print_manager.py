import os
import sys
import subprocess
from tkinter import messagebox


def open_file(path):
    if not path:
        messagebox.showerror("خطأ", "لا يوجد ملف لفتحه")
        return

    if not os.path.exists(path):
        messagebox.showerror("خطأ", f"الملف غير موجود:\n{path}")
        return

    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform.startswith("darwin"):
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("خطأ", f"تعذر فتح الملف:\n{e}")


def print_file(path):
    """
    طباعة مباشرة على Windows.
    في الأنظمة الأخرى يفتح الملف ليتم طباعته يدويا.
    """

    if not path:
        messagebox.showerror("خطأ", "لا يوجد ملف للطباعة")
        return

    if not os.path.exists(path):
        messagebox.showerror("خطأ", f"الملف غير موجود:\n{path}")
        return

    try:
        if sys.platform.startswith("win"):
            os.startfile(path, "print")
        else:
            open_file(path)

    except Exception as e:
        messagebox.showerror(
            "خطأ",
            f"تعذر إرسال الملف للطابعة:\n{e}\n\nسيتم فتح الملف للطباعة اليدوية."
        )
        open_file(path)
      
