import os
import subprocess
import sys
import customtkinter as ctk
from tkinter import messagebox

from database import search_archive


def open_file(path):
    try:
        if not path:
            return

        if not os.path.exists(path):
            messagebox.showerror(
                "خطأ",
                f"الملف غير موجود:\n{path}"
            )
            return

        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform.startswith("darwin"):
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])

    except Exception as e:
        messagebox.showerror(
            "خطأ",
            f"تعذر فتح الملف:\n{e}"
        )


class ArchivePage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.build_ui()

    def build_ui(self):

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.pack(fill="x", pady=(10, 20))

        title = ctk.CTkLabel(
            header,
            text="🗂️ الأرشيف",
            font=("Segoe UI", 30, "bold")
        )
        title.pack(side="right")

        self.search_entry = ctk.CTkEntry(
            header,
            placeholder_text="بحث باسم الزبون أو الوثيقة...",
            width=320,
            height=40,
            font=("Segoe UI", 14)
        )
        self.search_entry.pack(side="left", padx=10)

        search_btn = ctk.CTkButton(
            header,
            text="بحث",
            width=90,
            height=40,
            command=self.refresh_archive
        )
        search_btn.pack(side="left")

        self.stats_label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 14),
            text_color="#6B7280"
        )
        self.stats_label.pack(anchor="e", pady=(0, 10))

        self.results_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.results_frame.pack(fill="both", expand=True)

        self.refresh_archive()

    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def refresh_archive(self):

        self.clear_results()

        keyword = self.search_entry.get().strip()

        results = search_archive(keyword)

        self.stats_label.configure(
            text=f"عدد النتائج: {len(results)}"
        )

        if not results:
            empty = ctk.CTkLabel(
                self.results_frame,
                text="لا توجد نتائج.",
                font=("Segoe UI", 18),
                text_color="#6B7280"
            )
            empty.pack(pady=100)
            return

        for row in results:

            archive_id = row[0]
            customer_name = row[1]
            phone = row[2]
            document_type = row[3]
            template_name = row[4]
            word_path = row[5]
            pdf_path = row[6]
            created_at = row[7]

            card = ctk.CTkFrame(
                self.results_frame,
                corner_radius=18,
                fg_color="#F3F4F6"
            )
            card.pack(fill="x", padx=10, pady=10)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=18, pady=(15, 8))

            name_label = ctk.CTkLabel(
                top,
                text=f"👤 {customer_name or 'غير محدد'}",
                font=("Segoe UI", 18, "bold"),
                text_color="#111827"
            )
            name_label.pack(side="right")

            date_label = ctk.CTkLabel(
                top,
                text=created_at,
                font=("Segoe UI", 13),
                text_color="#6B7280"
            )
            date_label.pack(side="left")

            info = ctk.CTkLabel(
                card,
                text=(
                    f"📄 نوع الوثيقة: {document_type}\n"
                    f"🧩 النموذج: {template_name}\n"
                    f"📞 الهاتف: {phone or 'غير متوفر'}"
                ),
                justify="right",
                anchor="e",
                font=("Segoe UI", 14)
            )
            info.pack(fill="x", padx=18)

            actions = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )
            actions.pack(fill="x", padx=18, pady=(12, 15))

            open_word_btn = ctk.CTkButton(
                actions,
                text="📄 فتح Word",
                width=140,
                height=36,
                command=lambda p=word_path: open_file(p)
            )
            open_word_btn.pack(side="right", padx=5)

            if pdf_path:
                open_pdf_btn = ctk.CTkButton(
                    actions,
                    text="📕 فتح PDF",
                    width=140,
                    height=36,
                    command=lambda p=pdf_path: open_file(p)
                )
                open_pdf_btn.pack(side="right", padx=5)
