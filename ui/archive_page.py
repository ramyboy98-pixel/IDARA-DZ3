import os
import customtkinter as ctk
from tkinter import ttk, messagebox

from database import search_archive
from print_manager import open_file, print_file


class ArchivePage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.archive_rows = {}

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

        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", pady=(0, 12))

        open_word_btn = ctk.CTkButton(
            action_bar,
            text="📄 فتح Word",
            width=130,
            height=38,
            command=self.open_selected_word
        )
        open_word_btn.pack(side="right", padx=5)

        open_pdf_btn = ctk.CTkButton(
            action_bar,
            text="📕 فتح PDF",
            width=130,
            height=38,
            command=self.open_selected_pdf
        )
        open_pdf_btn.pack(side="right", padx=5)

        print_btn = ctk.CTkButton(
            action_bar,
            text="🖨️ طباعة",
            width=130,
            height=38,
            fg_color="#059669",
            hover_color="#047857",
            command=self.print_selected
        )
        print_btn.pack(side="right", padx=5)

        container = ctk.CTkFrame(
            self,
            corner_radius=22,
            fg_color="#FFFFFF"
        )
        container.pack(fill="both", expand=True)

        style = ttk.Style()

        try:
            style.theme_use("default")
        except Exception:
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

        self.tree.bind("<Double-1>", lambda e: self.open_selected_word())

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", pady=(10, 0))

        info = ctk.CTkLabel(
            bottom,
            text="اختر سطرا ثم استعمل أزرار الفتح أو الطباعة. النقر المزدوج يفتح Word.",
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

    def get_selected_row(self):

        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("تنبيه", "اختر وثيقة من الأرشيف أولا")
            return None

        item_id = selected[0]
        return self.archive_rows.get(item_id)

    def open_selected_word(self):

        row = self.get_selected_row()

        if not row:
            return

        word_path = row[5]
        open_file(word_path)

    def open_selected_pdf(self):

        row = self.get_selected_row()

        if not row:
            return

        pdf_path = row[6]
        open_file(pdf_path)

    def print_selected(self):

        row = self.get_selected_row()

        if not row:
            return

        word_path = row[5]
        pdf_path = row[6]

        if pdf_path and os.path.exists(pdf_path):
            print_file(pdf_path)
        elif word_path and os.path.exists(word_path):
            print_file(word_path)
        else:
            messagebox.showerror("خطأ", "لا يوجد ملف صالح للطباعة")
