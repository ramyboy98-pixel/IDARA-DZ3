# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from tkinter import messagebox


def open_file(path):
    """فتح ملف باستخدام التطبيق الافتراضي للنظام."""
    if not path:
        messagebox.showerror("خطأ", "لم يتم تحديد مسار الملف")
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
        messagebox.showerror("خطأ", f"فشل فتح الملف:\n{e}")


def print_file(path):
    """
    طباعة ملف باستخدام Windows.
    في الأنظمة الأخرى، يتم فتح الملف بالتطبيق الافتراضي للنظام.
    """

    if not path:
        messagebox.showerror("خطأ", "لم يتم تحديد ملف للطباعة")
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
            f"فشل في طباعة الملف:\n{e}\n\nسيتم فتح الملف بدلاً من ذلك"
        )
        open_file(path)
