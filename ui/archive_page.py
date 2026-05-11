import os
import sys
import subprocess
import customtkinter as ctk
from tkinter import ttk

from database import search_archive


def open_file(path):
    try:
        if not path:
            return

        if not os.path.exists(path):
            return

        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform.startswith("darwin"):
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])

    except Exception:
        pass


class ArchivePage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.build_ui()
        self.load_archive()

    def build_ui(self):

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 20))

        title = ctk.CTkLabel(
            header,
            text="🗂️ الأرشيف",
            font=("Segoe UI", 30, "bold"),
            text_color="#111827"
        )
        title.pack(side="right")

        self.search_entry = ctk.CTkEntry(
            header,
            placeholder_text="بحث باسم الزبون أو نوع الوثيقة أو الهاتف...",
            width=360,
            height=42,
            font=("Segoe UI", 14)
        )
        self.search_entry.pack(side="left", padx=10)

        self.search_entry.bind("<KeyRelease>", lambda e: self.load_archive())

        container = ctk.CTkFrame(
            self,
            corner_radius=22,
            fg_color="#FFFFFF"
        )
        container.pack(fill="both", expand=True)

        style = ttk.Style()

        try:
            style.theme_use("default")
        except:
            pass

        style.configure(
            "Treeview",
            rowheight=36,
            font=("Segoe UI", 11),
            background="#FFFFFF",
            fieldbackground="#FFFFFF"
        )

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 11, "bold")
        )

        columns = (
            "customer",
            "phone",
            "document",
            "template",
            "date"
        )

        self.tree = ttk.Treeview(
            container,
            columns=columns,
            show="headings"
        )

        self.tree.heading("customer", text="الزبون")
        self.tree.heading("phone", text="الهاتف")
        self.tree.heading("document", text="القسم")
        self.tree.heading("template", text="النموذج")
        self.tree.heading("date", text="التاريخ")

        self.tree.column("customer", width=200, anchor="center")
        self.tree.column("phone", width=120, anchor="center")
        self.tree.column("document", width=150, anchor="center")
        self.tree.column("template", width=200, anchor="center")
        self.tree.column("date", width=180, anchor="center")

        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(18, 0), pady=18)
        scrollbar.pack(side="right", fill="y", pady=18, padx=(0, 18))

        self.tree.bind("<Double-1>", self.open_selected_document)

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", pady=(10, 0))

        info = ctk.CTkLabel(
            bottom,
            text="انقر مرتين على أي سطر لفتح ملف Word.",
            font=("Segoe UI", 13),
            text_color="#6B7280"
        )
        info.pack(side="right")

    def load_archive(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        keyword = self.search_entry.get().strip()

        rows = search_archive(keyword)

        self.archive_rows = {}

        for row in rows:

            (
                archive_id,
                customer_name,
                phone,
                document_type,
                template_name,
                word_path,
                pdf_path,
                created_at
            ) = row

            item_id = self.tree.insert(
                "",
                "end",
                values=(
                    customer_name,
                    phone,
                    document_type,
                    template_name,
                    created_at
                )
            )

            self.archive_rows[item_id] = row

    def open_selected_document(self, event):

        selected = self.tree.selection()

        if not selected:
            return

        item_id = selected[0]

        row = self.archive_rows.get(item_id)

        if not row:
            return

        word_path = row[5]
        pdf_path = row[6]

        if word_path and os.path.exists(word_path):
            open_file(word_path)
        elif pdf_path and os.path.exists(pdf_path):
            open_file(pdf_path)
