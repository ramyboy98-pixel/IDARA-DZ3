import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

from backup_manager import create_backup, restore_backup, list_backups

BG = "#F5F7FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"
BLUE = "#2563EB"
GREEN = "#059669"
GRAY = "#6B7280"


class SettingsPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(8, 16))

        ctk.CTkLabel(
            header,
            text="الإعدادات",
            font=("Segoe UI", 30, "bold"),
            text_color=TEXT,
        ).pack(anchor="e")

        ctk.CTkLabel(
            header,
            text="إدارة النسخ الاحتياطية وحماية بيانات البرنامج.",
            font=("Segoe UI", 14),
            text_color=MUTED,
        ).pack(anchor="e", pady=(6, 0))

        backup_card = ctk.CTkFrame(
            self,
            corner_radius=22,
            fg_color=CARD,
            border_width=1,
            border_color=BORDER,
        )
        backup_card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            backup_card,
            text="النسخ الاحتياطي",
            font=("Segoe UI", 22, "bold"),
            text_color=TEXT,
        ).pack(anchor="e", padx=24, pady=(22, 8))

        ctk.CTkLabel(
            backup_card,
            text="احفظ نسخة من قاعدة البيانات والملفات المهمة، أو استعد نسخة قديمة عند الحاجة.",
            font=("Segoe UI", 14),
            text_color=MUTED,
            justify="right",
        ).pack(anchor="e", padx=24, pady=(0, 18))

        buttons = ctk.CTkFrame(backup_card, fg_color="transparent")
        buttons.pack(fill="x", padx=24, pady=(0, 22))

        ctk.CTkButton(
            buttons,
            text="إنشاء نسخة احتياطية",
            height=42,
            font=("Segoe UI", 15, "bold"),
            fg_color=BLUE,
            hover_color="#1D4ED8",
            command=self.create_backup_action,
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            buttons,
            text="استعادة نسخة",
            height=42,
            font=("Segoe UI", 15, "bold"),
            fg_color=GREEN,
            hover_color="#047857",
            command=self.restore_backup_action,
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            buttons,
            text="تحديث القائمة",
            height=42,
            font=("Segoe UI", 15, "bold"),
            fg_color=GRAY,
            hover_color="#4B5563",
            command=self.load_backups,
        ).pack(side="right", padx=5)

        self.backups_area = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )
        self.backups_area.pack(fill="both", expand=True)

        self.load_backups()

    def create_backup_action(self):
        try:
            path = create_backup()
            messagebox.showinfo("تم", f"تم إنشاء النسخة الاحتياطية بنجاح:\n{path}")
            self.load_backups()
        except Exception as e:
            messagebox.showerror("خطأ", f"تعذر إنشاء النسخة الاحتياطية:\n{e}")

    def restore_backup_action(self):
        backup_path = filedialog.askopenfilename(
            title="اختر ملف النسخة الاحتياطية",
            filetypes=[("Backup ZIP", "*.zip"), ("كل الملفات", "*.*")],
        )

        if not backup_path:
            return

        answer = messagebox.askyesno(
            "تأكيد الاستعادة",
            "هل أنت متأكد من استعادة هذه النسخة؟\nقد يتم استبدال ملفات حالية.",
        )

        if not answer:
            return

        try:
            restore_backup(backup_path)
            messagebox.showinfo("تم", "تمت استعادة النسخة الاحتياطية بنجاح.\nأغلق البرنامج وافتحه من جديد.")
        except Exception as e:
            messagebox.showerror("خطأ", f"تعذر استعادة النسخة:\n{e}")

    def load_backups(self):
        for widget in self.backups_area.winfo_children():
            widget.destroy()

        backups = list_backups()

        if not backups:
            empty = ctk.CTkFrame(
                self.backups_area,
                fg_color=CARD,
                corner_radius=20,
                border_width=1,
                border_color=BORDER,
            )
            empty.pack(fill="x", pady=(0, 10))
            ctk.CTkLabel(
                empty,
                text="لا توجد نسخ احتياطية بعد.",
                font=("Segoe UI", 17, "bold"),
                text_color=TEXT,
            ).pack(pady=(28, 6))
            ctk.CTkLabel(
                empty,
                text="اضغط على إنشاء نسخة احتياطية لحفظ بياناتك.",
                font=("Segoe UI", 13),
                text_color=MUTED,
            ).pack(pady=(0, 28))
            return

        for file_name, path, modified in backups:
            self.backup_card(file_name, path, modified)

    def backup_card(self, file_name, path, modified):
        card = ctk.CTkFrame(
            self.backups_area,
            corner_radius=18,
            fg_color=CARD,
            border_width=1,
            border_color=BORDER,
        )
        card.pack(fill="x", pady=7)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="right", fill="both", expand=True, padx=18, pady=12)

        ctk.CTkLabel(
            info,
            text=file_name,
            justify="right",
            anchor="e",
            font=("Segoe UI", 15, "bold"),
            text_color=TEXT,
        ).pack(anchor="e")

        ctk.CTkLabel(
            info,
            text=f"المسار: {path}\nآخر تعديل: {modified}",
            justify="right",
            anchor="e",
            font=("Segoe UI", 12),
            text_color=MUTED,
            wraplength=720,
        ).pack(anchor="e", pady=(4, 0))

        ctk.CTkButton(
            card,
            text="فتح المجلد",
            width=120,
            height=36,
            fg_color="#F3F4F6",
            hover_color="#E5E7EB",
            text_color=TEXT,
            command=lambda p=path: self.open_folder(p),
        ).pack(side="left", padx=18)

    def open_folder(self, path):
        folder = os.path.dirname(path)
        try:
            os.startfile(folder)
        except Exception:
            messagebox.showinfo("المسار", folder)
