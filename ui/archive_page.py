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
        header.pack(fill="x", pady=(10, 12))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="right", fill="x", expand=True)
        ctk.CTkLabel(title_box, text="ًں—‚ï¸ڈ ط§ظ„ط£ط±ط´ظٹظپ", font=("Segoe UI", 30, "bold"), text_color=TEXT).pack(anchor="e")
        ctk.CTkLabel(title_box, text="ط¨ط­ط«طŒ ظپظ„طھط±ط©طŒ ظپطھط­ ظˆط¥ط¹ط§ط¯ط© ط·ط¨ط§ط¹ط© ط§ظ„ظˆط«ط§ط¦ظ‚ ط§ظ„ظ…ط­ظپظˆط¸ط©.", font=("Segoe UI", 14), text_color=MUTED).pack(anchor="e", pady=(5, 0))

        filters = ctk.CTkFrame(self, corner_radius=20, fg_color=CARD, border_width=1, border_color=BORDER)
        filters.pack(fill="x", pady=(0, 8), anchor="n")

        self.search_entry = ctk.CTkEntry(filters, placeholder_text="ط¨ط­ط« ط¨ط§ط³ظ… ط§ظ„ط²ط¨ظˆظ† ط£ظˆ ط§ظ„ظˆط«ظٹظ‚ط© ط£ظˆ ط§ظ„ظ‡ط§طھظپ...", width=340, height=40, font=("Segoe UI", 14))
        self.search_entry.pack(side="right", padx=14, pady=14)
        self.search_entry.bind("<KeyRelease>", self.on_search_key)

        self.date_from_entry = ctk.CTkEntry(filters, placeholder_text="ظ…ظ† طھط§ط±ظٹط® YYYY-MM-DD", width=165, height=40, font=("Segoe UI", 13))
        self.date_from_entry.pack(side="right", padx=5, pady=14)
        self.date_from_entry.bind("<KeyRelease>", lambda e: self.load_archive())

        self.date_to_entry = ctk.CTkEntry(filters, placeholder_text="ط¥ظ„ظ‰ طھط§ط±ظٹط® YYYY-MM-DD", width=165, height=40, font=("Segoe UI", 13))
        self.date_to_entry.pack(side="right", padx=5, pady=14)
        self.date_to_entry.bind("<KeyRelease>", lambda e: self.load_archive())

        clear_btn = ctk.CTkButton(filters, text="ظ…ط³ط­ ط§ظ„ظپظ„طھط±", width=115, height=40, fg_color="#6B7280", hover_color="#4B5563", command=self.clear_filters)
        clear_btn.pack(side="left", padx=14, pady=14)

        # طµظ†ط¯ظˆظ‚ ط§ظ„ط§ظ‚طھط±ط§ط­ط§طھ ظ„ط§ ظٹط¸ظ‡ط± ظˆظ‡ظˆ ظپط§ط±ط؛ ط­طھظ‰ ظ„ط§ ظٹط¯ظپط¹ ط¬ط¯ظˆظ„ ط§ظ„ط£ط±ط´ظٹظپ ظ„ظ„ط£ط³ظپظ„.
        self.suggestions_box = ctk.CTkFrame(self, fg_color="transparent", height=1)

        self.action_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.action_bar.pack(fill="x", pady=(0, 8), anchor="n")

        ctk.CTkButton(self.action_bar, text="ًں“„ ظپطھط­ ظ…ظ„ظپ ظˆظˆط±ط¯", width=130, height=38, command=self.open_selected_word).pack(side="right", padx=5)
        ctk.CTkButton(self.action_bar, text="ًں“• ظپطھط­ PDF", width=130, height=38, command=self.open_selected_pdf).pack(side="right", padx=5)
        ctk.CTkButton(self.action_bar, text="ًں–¨ï¸ڈ ط·ط¨ط§ط¹ط©", width=130, height=38, fg_color=GREEN, hover_color="#047857", command=self.print_selected).pack(side="right", padx=5)
        self.count_label = ctk.CTkLabel(self.action_bar, text="", font=("Segoe UI", 13), text_color=MUTED)
        self.count_label.pack(side="left", padx=8)

        container = ctk.CTkFrame(self, corner_radius=18, fg_color=CARD, border_width=1, border_color=BORDER)
        # ط¬ط¯ظˆظ„ ط§ظ„ط£ط±ط´ظٹظپ ظ…ط«ط¨طھ ظ…ط¨ط§ط´ط±ط© طھط­طھ ط§ظ„ط£ط²ط±ط§ط±طŒ ط¨ط¯ظˆظ† طھظ…ط¯ط¯ ظٹط¯ظپط¹ظ‡ ظ„ظ„ط£ط³ظپظ„.
        container.pack(fill="x", expand=False, anchor="n", pady=(0, 0))
        container.configure(height=430)
        container.pack_propagate(False)

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
            "customer": "ط§ظ„ط²ط¨ظˆظ†",
            "phone": "ط§ظ„ظ‡ط§طھظپ",
            "document": "ط§ظ„ظ‚ط³ظ…",
            "template": "ط§ظ„ظ†ظ…ظˆط°ط¬",
            "date": "ط§ظ„طھط§ط±ظٹط®",
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



    def on_search_key(self, event=None):
        self.load_archive_suggestions()
        self.load_archive()

    def load_archive_suggestions(self):
        if not self.suggestions_box:
            return
        for widget in self.suggestions_box.winfo_children():
            widget.destroy()
        self.suggestions_box.pack_forget()
        keyword = self.search_entry.get().strip()
        if not keyword:
            return
        try:
            rows = search_archive(keyword)[:6]
        except Exception:
            rows = []
        if not rows:
            return
        try:
            self.suggestions_box.pack(fill="x", pady=(0, 8), before=self.action_bar)
        except Exception:
            self.suggestions_box.pack(fill="x", pady=(0, 8))
        box = ctk.CTkFrame(self.suggestions_box, fg_color="#FFFFFF", corner_radius=14, border_width=1, border_color=BORDER)
        box.pack(fill="x")
        for row in rows:
            _id, customer_name, phone, document_type, template_name, word_path, pdf_path, created_at = row
            title = template_name or customer_name or phone
            subtitle = f"{customer_name or ''} {phone or ''}".strip()
            btn = ctk.CTkButton(
                box,
                text=f"{title}  â€”  {subtitle}",
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
            self.suggestions_box.pack_forget()
        self.load_archive()

    def clear_filters(self):
        self.search_entry.delete(0, "end")
        self.date_from_entry.delete(0, "end")
        self.date_to_entry.delete(0, "end")
        if self.suggestions_box:
            for widget in self.suggestions_box.winfo_children():
                widget.destroy()
            self.suggestions_box.pack_forget()
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
        self.count_label.configure(text=f"ط¹ط¯ط¯ ط§ظ„ظ†طھط§ط¦ط¬: {len(rows)}")

    def get_selected_row(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("طھظ†ط¨ظٹظ‡", "ط§ط®طھط± ظˆط«ظٹظ‚ط© ظ…ظ† ط§ظ„ط£ط±ط´ظٹظپ ط£ظˆظ„ط§")
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
            messagebox.showerror("ط®ط·ط£", "ظ„ط§ ظٹظˆط¬ط¯ ظ…ظ„ظپ طµط§ظ„ط­ ظ„ظ„ط·ط¨ط§ط¹ط©")
