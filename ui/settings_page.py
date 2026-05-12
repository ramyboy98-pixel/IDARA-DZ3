import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

from backup_manager import create_backup, restore_backup, list_backups


class SettingsPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.build_ui()

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="⚙️ الإعدادات",
            font=("Segoe UI", 30, "bold"),
            text_color="#111827"
        )
        title.pack(anchor="e", pady=(10, 20))

        backup_card = ctk.CTkFrame(
            self,
            corner_radius=22,
            fg_color="#FFFFFF"
        )
        backup_card.pack(fill="x", padx=10, pady=10)

        backup_title = ctk.CTkLabel(
            backup_card,
            text="🛡️ النسخ الاحتياطي",
            font=("Segoe UI", 22, "bold"),
            text_color="#111827"
        )
        backup_title.pack(anchor="e", padx=24, pady=(22, 8))

        backup_desc = ctk.CTkLabel(
            backup_card,
            text="احفظ نسخة احتياطية من قاعدة البيانات، النماذج، والوثائق الناتجة حتى لا تضيع بياناتك.",
            font=("Segoe UI", 14),
            text_color="#6B7280",
            justify="right"
        )
        backup_desc.pack(anchor="e", padx=24, pady=(0, 18))

        buttons = ctk.CTkFrame(
            backup_card,
            fg_color="transparent"
        )
        buttons.pack(fill="x", padx=24, pady=(0, 22))

        create_btn = ctk.CTkButton(
            buttons,
            text="📦 إنشاء نسخة احتياطية",
            height=42,
            font=("Segoe UI", 15, "bold"),
            command=self.create_backup_action
        )
        create_btn.pack(side="right", padx=5)

        restore_btn = ctk.CTkButton(
            buttons,
            text="♻️ استعادة نسخة",
            height=42,
            font=("Segoe UI", 15, "bold"),
            fg_color="#059669",
            hover_color="#047857",
            command=self.restore_backup_action
        )
        restore_btn.pack(side="right", padx=5)

        refresh_btn = ctk.CTkButton(
            buttons,
            text="🔄 تحديث القائمة",
            height=42,
            font=("Segoe UI", 15, "bold"),
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.load_backups
        )
        refresh_btn.pack(side="right", padx=5)

        self.backups_area = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.backups_area.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_backups()

    def create_backup_action(self):
        try:
            path = create_backup()

            messagebox.showinfo(
                "تم",
                f"تم إنشاء النسخة الاحتياطية بنجاح:\n{path}"
            )

            self.load_backups()

        except Exception as e:
            messagebox.showerror(
                "خطأ",
                f"تعذر إنشاء النسخة الاحتياطية:\n{e}"
            )

    def restore_backup_action(self):

        backup_path = filedialog.askopenfilename(
            title="اختر ملف النسخة الاحتياطية",
            filetypes=[
                ("Backup ZIP", "*.zip"),
                ("كل الملفات", "*.*")
            ]
        )

        if not backup_path:
            return

        answer = messagebox.askyesno(
            "تأكيد الاستعادة",
            "هل أنت متأكد من استعادة هذه النسخة؟\nقد يتم استبدال ملفات حالية."
        )

        if not answer:
            return

        try:
            restore_backup(backup_path)

            messagebox.showinfo(
                "تم",
                "تمت استعادة النسخة الاحتياطية بنجاح.\nأغلق البرنامج وافتحه من جديد."
            )

        except Exception as e:
            messagebox.showerror(
                "خطأ",
                f"تعذر استعادة النسخة:\n{e}"
            )

    def load_backups(self):

        for widget in self.backups_area.winfo_children():
            widget.destroy()

        backups = list_backups()

        if not backups:
            empty = ctk.CTkLabel(
                self.backups_area,
                text="لا توجد نسخ احتياطية بعد.",
                font=("Segoe UI", 17),
                text_color="#6B7280"
            )
            empty.pack(pady=70)
            return

        for file_name, path, modified in backups:

            card = ctk.CTkFrame(
                self.backups_area,
                corner_radius=18,
                fg_color="#FFFFFF"
            )
            card.pack(fill="x", pady=8)

            info = ctk.CTkLabel(
                card,
                text=f"📦 {file_name}\n📁 {path}",
                justify="right",
                anchor="e",
                font=("Segoe UI", 14),
                text_color="#111827"
            )
            info.pack(side="right", fill="x", expand=True, padx=18, pady=14)

            open_btn = ctk.CTkButton(
                card,
                text="فتح المجلد",
                width=120,
                height=36,
                command=lambda p=path: self.open_folder(p)
            )
            open_btn.pack(side="left", padx=18)

    def open_folder(self, path):

        folder = os.path.dirname(path)

        try:
            os.startfile(folder)
        except Exception:
            messagebox.showinfo(
                "المسار",
                folder
            )
