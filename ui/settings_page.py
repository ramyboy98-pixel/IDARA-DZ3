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
            text="âڑ™ï¸ڈ ط§ظ„ط¥ط¹ط¯ط§ط¯ط§طھ",
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
            text="ًں›،ï¸ڈ ط§ظ„ظ†ط³ط® ط§ظ„ط§ط­طھظٹط§ط·ظٹ",
            font=("Segoe UI", 22, "bold"),
            text_color="#111827"
        )
        backup_title.pack(anchor="e", padx=24, pady=(22, 8))

        backup_desc = ctk.CTkLabel(
            backup_card,
            text="ط§ط­ظپط¸ ظ†ط³ط®ط© ط§ط­طھظٹط§ط·ظٹط© ظ…ظ† ظ‚ط§ط¹ط¯ط© ط§ظ„ط¨ظٹط§ظ†ط§طھطŒ ط§ظ„ظ†ظ…ط§ط°ط¬طŒ ظˆط§ظ„ظˆط«ط§ط¦ظ‚ ط§ظ„ظ†ط§طھط¬ط© ط­طھظ‰ ظ„ط§ طھط¶ظٹط¹ ط¨ظٹط§ظ†ط§طھظƒ.",
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
            text="ًں“¦ ط¥ظ†ط´ط§ط، ظ†ط³ط®ط© ط§ط­طھظٹط§ط·ظٹط©",
            height=42,
            font=("Segoe UI", 15, "bold"),
            command=self.create_backup_action
        )
        create_btn.pack(side="right", padx=5)

        restore_btn = ctk.CTkButton(
            buttons,
            text="â™»ï¸ڈ ط§ط³طھط¹ط§ط¯ط© ظ†ط³ط®ط©",
            height=42,
            font=("Segoe UI", 15, "bold"),
            fg_color="#059669",
            hover_color="#047857",
            command=self.restore_backup_action
        )
        restore_btn.pack(side="right", padx=5)

        refresh_btn = ctk.CTkButton(
            buttons,
            text="ًں”„ طھط­ط¯ظٹط« ط§ظ„ظ‚ط§ط¦ظ…ط©",
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
                "طھظ…",
                f"طھظ… ط¥ظ†ط´ط§ط، ط§ظ„ظ†ط³ط®ط© ط§ظ„ط§ط­طھظٹط§ط·ظٹط© ط¨ظ†ط¬ط§ط­:\n{path}"
            )

            self.load_backups()

        except Exception as e:
            messagebox.showerror(
                "ط®ط·ط£",
                f"طھط¹ط°ط± ط¥ظ†ط´ط§ط، ط§ظ„ظ†ط³ط®ط© ط§ظ„ط§ط­طھظٹط§ط·ظٹط©:\n{e}"
            )

    def restore_backup_action(self):

        backup_path = filedialog.askopenfilename(
            title="ط§ط®طھط± ظ…ظ„ظپ ط§ظ„ظ†ط³ط®ط© ط§ظ„ط§ط­طھظٹط§ط·ظٹط©",
            filetypes=[
                ("Backup ZIP", "*.zip"),
                ("ظƒظ„ ط§ظ„ظ…ظ„ظپط§طھ", "*.*")
            ]
        )

        if not backup_path:
            return

        answer = messagebox.askyesno(
            "طھط£ظƒظٹط¯ ط§ظ„ط§ط³طھط¹ط§ط¯ط©",
            "ظ‡ظ„ ط£ظ†طھ ظ…طھط£ظƒط¯ ظ…ظ† ط§ط³طھط¹ط§ط¯ط© ظ‡ط°ظ‡ ط§ظ„ظ†ط³ط®ط©طں\nظ‚ط¯ ظٹطھظ… ط§ط³طھط¨ط¯ط§ظ„ ظ…ظ„ظپط§طھ ط­ط§ظ„ظٹط©."
        )

        if not answer:
            return

        try:
            restore_backup(backup_path)

            messagebox.showinfo(
                "طھظ…",
                "طھظ…طھ ط§ط³طھط¹ط§ط¯ط© ط§ظ„ظ†ط³ط®ط© ط§ظ„ط§ط­طھظٹط§ط·ظٹط© ط¨ظ†ط¬ط§ط­.\nط£ط؛ظ„ظ‚ ط§ظ„ط¨ط±ظ†ط§ظ…ط¬ ظˆط§ظپطھط­ظ‡ ظ…ظ† ط¬ط¯ظٹط¯."
            )

        except Exception as e:
            messagebox.showerror(
                "ط®ط·ط£",
                f"طھط¹ط°ط± ط§ط³طھط¹ط§ط¯ط© ط§ظ„ظ†ط³ط®ط©:\n{e}"
            )

    def load_backups(self):

        for widget in self.backups_area.winfo_children():
            widget.destroy()

        backups = list_backups()

        if not backups:
            empty = ctk.CTkLabel(
                self.backups_area,
                text="ظ„ط§ طھظˆط¬ط¯ ظ†ط³ط® ط§ط­طھظٹط§ط·ظٹط© ط¨ط¹ط¯.",
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
                text=f"ًں“¦ {file_name}\nًں“پ {path}",
                justify="right",
                anchor="e",
                font=("Segoe UI", 14),
                text_color="#111827"
            )
            info.pack(side="right", fill="x", expand=True, padx=18, pady=14)

            open_btn = ctk.CTkButton(
                card,
                text="ظپطھط­ ط§ظ„ظ…ط¬ظ„ط¯",
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
                "ط§ظ„ظ…ط³ط§ط±",
                folder
            )
