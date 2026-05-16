import os
import customtkinter as ctk
from tkinter import ttk, messagebox

from database import search_archive
from print_manager import open_file, print_file

BG = "#F5F7FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"
GREEN = "#059669"


class ArchivePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.archive_rows = {}
        self.suggestions_box = None
        self.build_ui()
        self.load_archive()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 18))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="right", fill="x", expand=True)
        ctk.CTkLabel(title_box, text="🗂️ الأرشيف", font=("Segoe UI", 30, "bold"), text_color=TEXT).pack(anchor="e")
        ctk.CTkLabel(title_box, text="بحث، فلترة، فتح وإعادة طباعة الوثائق المحفوظة.", font=("Segoe UI", 14), text_color=MUTED).pack(anchor="e", pady=(5, 0))

        filters = ctk.CTkFrame(self, corner_radius=20, fg_color=CARD, border_width=1, border_color=BORDER)
        filters.pack(fill="x", pady=(0, 12))

        self.search_entry = ctk.CTkEntry(filters, placeholder_text="بحث باسم الزبون أو الوثيقة أو الهاتف...", width=340, height=40, font=("Segoe UI", 14))
        self.search_entry.pack(side="right", padx=14, pady=14)
        self.search_entry.bind("<KeyRelease>", self.on_search_key)

        self.date_from_entry = ctk.CTkEntry(filters, placeholder_text="من تاريخ YYYY-MM-DD", width=165, height=40, font=("Segoe UI", 13))
        self.date_from_entry.pack(side="right", padx=5, pady=14)
        self.date_from_entry.bind("<KeyRelease>", lambda e: self.load_archive())

        self.date_to_entry = ctk.CTkEntry(filters, placeholder_text="إلى تاريخ YYYY-MM-DD", width=165, height=40, font=("Segoe UI", 13))
        self.date_to_entry.pack(side="right", padx=5, pady=14)
        self.date_to_entry.bind("<KeyRelease>", lambda e: self.load_archive())

        clear_btn = ctk.CTkButton(filters, text="مسح الفلتر", width=115, height=40, fg_color="#6B7280", hover_color="#4B5563", command=self.clear_filters)
        clear_btn.pack(side="left", padx=14, pady=14)

        self.suggestions_box = ctk.CTkFrame(self, fg_color="transparent")
        self.suggestions_box.pack(fill="x", pady=(0, 8))

        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", pady=(0, 12))

        ctk.CTkButton(action_bar, text="📄 فتح ملف وورد", width=130, height=38, command=self.open_selected_word).pack(side="right", padx=5)
        ctk.CTkButton(action_bar, text="📕 فتح PDF", width=130, height=38, command=self.open_selected_pdf).pack(side="right", padx=5)
        ctk.CTkButton(action_bar, text="🖨️ طباعة", width=130, height=38, fg_color=GREEN, hover_color="#047857", command=self.print_selected).pack(side="right", padx=5)
        self.count_label = ctk.CTkLabel(action_bar, text="", font=("Segoe UI", 13), text_color=MUTED)
        self.count_label.pack(side="left", padx=8)

        container = ctk.CTkFrame(self, corner_radius=22, fg_color=CARD, border_width=1, border_color=BORDER)
        container.pack(fill="both", expand=True)

        style = ttk.Style()
        try:
            style.theme_use("default")
        except Exception:
            pass
        style.configure("Treeview", rowheight=36, font=("Segoe UI", 11), background="#FFFFFF", fieldbackground="#FFFFFF", borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

        columns = ("customer", "phone", "document", "template", "date")
        self.tree = ttk.Treeview(container, columns=columns, show="headings")
        headings = {
            "customer": "الزبون",
            "phone": "الهاتف",
            "document": "القسم",
            "template": "النموذج",
            "date": "التاريخ",
        }
        for key, text in headings.items():
            self.tree.heading(key, text=text)
            self.tree.column(key, anchor="center")
        self.tree.column("customer", width=200)
        self.tree.column("phone", width=120)
        self.tree.column("document", width=150)
        self.tree.column("template", width=220)
        self.tree.column("date", width=180)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(18, 0), pady=18)
        scrollbar.pack(side="right", fill="y", pady=18, padx=(0, 18))
        self.tree.bind("<Double-1>", lambda e: self.open_selected_word())

        info = ctk.CTkLabel(self, text="النقر المزدوج يفتح ملف وورد. استعمل صيغة التاريخ 2026-05-12 للفلترة.", font=("Segoe UI", 13), text_color=MUTED)
        info.pack(anchor="e", pady=(10, 0))


    def on_search_key(self, event=None):
        self.load_archive_suggestions()
        self.load_archive()

    def load_archive_suggestions(self):
        if not self.suggestions_box:
            return
        for widget in self.suggestions_box.winfo_children():
            widget.destroy()
        keyword = self.search_entry.get().strip()
        if not keyword:
            return
        try:
            rows = search_archive(keyword)[:6]
        except Exception:
            rows = []
        if not rows:
            return
        box = ctk.CTkFrame(self.suggestions_box, fg_color="#FFFFFF", corner_radius=14, border_width=1, border_color=BORDER)
        box.pack(fill="x")
        for row in rows:
            _id, customer_name, phone, document_type, template_name, word_path, pdf_path, created_at = row
            title = template_name or customer_name or phone
            subtitle = f"{customer_name or ''} {phone or ''}".strip()
            btn = ctk.CTkButton(
                box,
                text=f"{title}  —  {subtitle}",
                anchor="e",
                height=32,
                corner_radius=10,
                fg_color="transparent",
                hover_color="#EFF6FF",
                text_color=TEXT,
                font=("Segoe UI", 13),
                command=lambda value=title: self.choose_archive_suggestion(value),
            )
            btn.pack(fill="x", padx=8, pady=3)

    def choose_archive_suggestion(self, value):
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, value)
        if self.suggestions_box:
            for widget in self.suggestions_box.winfo_children():
                widget.destroy()
        self.load_archive()

    def clear_filters(self):
        self.search_entry.delete(0, "end")
        self.date_from_entry.delete(0, "end")
        self.date_to_entry.delete(0, "end")
        if self.suggestions_box:
            for widget in self.suggestions_box.winfo_children():
                widget.destroy()
        self.load_archive()

    def load_archive(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        keyword = self.search_entry.get().strip()
        date_from = self.date_from_entry.get().strip()
        date_to = self.date_to_entry.get().strip()
        rows = search_archive(keyword, date_from, date_to)
        self.archive_rows = {}
        for row in rows:
            archive_id, customer_name, phone, document_type, template_name, word_path, pdf_path, created_at = row
            item_id = self.tree.insert("", "end", values=(customer_name, phone, document_type, template_name, created_at))
            self.archive_rows[item_id] = row
        self.count_label.configure(text=f"عدد النتائج: {len(rows)}")

    def get_selected_row(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "اختر وثيقة من الأرشيف أولا")
            return None
        return self.archive_rows.get(selected[0])

    def open_selected_word(self):
        row = self.get_selected_row()
        if row:
            open_file(row[5])

    def open_selected_pdf(self):
        row = self.get_selected_row()
        if row:
            open_file(row[6])

    def print_selected(self):
        row = self.get_selected_row()
        if not row:
            return
        word_path, pdf_path = row[5], row[6]
        if pdf_path and os.path.exists(pdf_path):
            print_file(pdf_path)
        elif word_path and os.path.exists(word_path):
            print_file(word_path)
        else:
            messagebox.showerror("خطأ", "لا يوجد ملف صالح للطباعة")
