import os
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox

from utils.paths import get_templates_dir
from database import (
    init_database,
    get_categories,
    search_templates,
    get_template_fields,
    add_template,
    update_template,
    get_template,
    delete_template,
    make_field_key,
    save_archive,
    save_customer,
    search_customers,
)
from document_engine import (
    generate_word_document,
    generate_word_from_text_template,
    convert_word_to_pdf,
    render_text_template,
)
from print_manager import open_file, print_file

TEMPLATES_FOLDER = get_templates_dir()

BG = "#F5F7FA"
CARD = "#FFFFFF"
MUTED = "#6B7280"
TEXT = "#111827"
BORDER = "#E5E7EB"
BLUE = "#2563EB"
GREEN = "#059669"
RED = "#DC2626"
GRAY_BTN = "#F3F4F6"

DEFAULT_FIELDS = [
    "ط§ظ„ط§ط³ظ…", "ط§ظ„ظ„ظ‚ط¨", "طھط§ط±ظٹط® ط§ظ„ظ…ظٹظ„ط§ط¯", "ط§ظ„ط¹ظ†ظˆط§ظ†", "ط±ظ‚ظ… ط§ظ„ظ‡ط§طھظپ", "طھط§ط±ظٹط® ط§ظ„ط·ظ„ط¨",
    "ط§ظ„ط¬ظ‡ط© ط§ظ„ظ…ط±ط³ظ„ ط¥ظ„ظٹظ‡ط§", "ط§ظ„ظ…ظ†طµط¨", "ط§ظ„ط´ظ‡ط§ط¯ط©", "ط§ظ„طھط®طµطµ", "ط§ظ„ظ…ط³طھظˆظ‰ ط§ظ„ط¯ط±ط§ط³ظٹ", "ط§ظ„ط®ط¨ط±ط©",
    "ط§ظ„ط¬ط§ظ…ط¹ط©", "ظˆظ„ط§ظٹط© ط§ظ„ط¬ط§ظ…ط¹ط©", "ط§ظ„ط³ظ†ط© ط§ظ„ط¬ط§ظ…ط¹ظٹط©", "ط§ظ„ط¯ظپط¹ط©",
]


def ensure_templates_folder():
    os.makedirs(TEMPLATES_FOLDER, exist_ok=True)


def safe_template_file_name(name):
    value = str(name or "template").strip().replace(" ", "_")
    for char in '<>:"/\\|?*':
        value = value.replace(char, "_")
    return value or "template"


class DocumentsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        init_database()
        ensure_templates_folder()
        self.current_category_id = None
        self.current_category_name = None
        self.current_category_icon = None
        self.template_search_entry = None
        self.template_suggestions_area = None
        self.templates_area = None
        self.build_categories_ui()

    def clear_page(self):
        for widget in self.winfo_children():
            widget.destroy()

    def page_title(self, parent, title, subtitle=""):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(10, 20))
        box = ctk.CTkFrame(header, fg_color="transparent")
        box.pack(side="right", fill="x", expand=True)
        ctk.CTkLabel(box, text=title, font=("Segoe UI", 30, "bold"), text_color=TEXT).pack(anchor="e")
        if subtitle:
            ctk.CTkLabel(box, text=subtitle, font=("Segoe UI", 14), text_color=MUTED).pack(anchor="e", pady=(6, 0))
        return header

    def build_categories_ui(self):
        self.clear_page()
        self.page_title(
            self,
            "ًں“„ ظ‚ط³ظ… ط§ظ„ظˆط«ط§ط¦ظ‚",
            "ط§ط®طھط± ط§ظ„ظ‚ط³ظ…طŒ ط«ظ… ط£ظ†ط´ط¦ ظ†ظ…ط§ط°ط¬ ظˆظˆط±ط¯ ظˆط§ط³طھظ…ط§ط±ط§طھ ط®ط§طµط© ط¨ظƒظ„ ظˆط«ظٹظ‚ط©."
        )

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, pady=(15, 0))

        try:
            categories = get_categories()
        except Exception as e:
            messagebox.showerror("ط®ط·ط£", f"طھط¹ط°ط± طھط­ظ…ظٹظ„ ط§ظ„ط£ظ‚ط³ط§ظ…:\n{e}")
            categories = []

        for col in range(4):
            grid.grid_columnconfigure(col, weight=1, uniform="document_categories")

        visible_categories = [cat for cat in categories if cat[1] != "ط£ط®ط±ظ‰"]

        def bind_open(widget, cid, n, i):
            widget.bind("<Button-1>", lambda _event: self.open_category(cid, n, i))
            try:
                widget.configure(cursor="hand2")
            except Exception:
                pass

        def bind_hover(widget, on_enter, on_leave):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        for index, (category_id, name, icon) in enumerate(visible_categories):
            row, col = divmod(index, 4)
            card = ctk.CTkFrame(grid, corner_radius=24, fg_color=CARD, border_width=1, border_color=BORDER)
            card.grid(row=row, column=col, sticky="nsew", padx=10, pady=12)
            card.grid_propagate(False)
            card.configure(width=245, height=210)
            bind_open(card, category_id, name, icon)

            icon_label = ctk.CTkLabel(card, text=icon, font=("Segoe UI Emoji", 44))
            icon_label.pack(pady=(32, 10))
            bind_open(icon_label, category_id, name, icon)

            name_label = ctk.CTkLabel(card, text=name, font=("Segoe UI", 22, "bold"), text_color=TEXT)
            name_label.pack()
            bind_open(name_label, category_id, name, icon)

            subtitle = ctk.CTkLabel(card, text="ط¥ط¯ط§ط±ط© ط§ظ„ظ†ظ…ط§ط°ط¬ ظˆط§ظ„ط§ط³طھظ…ط§ط±ط§طھ", font=("Segoe UI", 12), text_color=MUTED)
            subtitle.pack(pady=(7, 0))
            bind_open(subtitle, category_id, name, icon)

            def make_enter(c=card, il=icon_label, nl=name_label, sl=subtitle):
                def _enter(_event=None):
                    c.configure(fg_color="#EFF6FF", border_color=BLUE)
                    il.configure(font=("Segoe UI Emoji", 50), text_color=BLUE)
                    nl.configure(text_color=BLUE)
                    sl.configure(text_color="#374151")
                return _enter

            def make_leave(c=card, il=icon_label, nl=name_label, sl=subtitle):
                def _leave(_event=None):
                    c.configure(fg_color=CARD, border_color=BORDER)
                    il.configure(font=("Segoe UI Emoji", 44), text_color=TEXT)
                    nl.configure(text_color=TEXT)
                    sl.configure(text_color=MUTED)
                return _leave

            on_enter = make_enter()
            on_leave = make_leave()
            for hover_widget in (card, icon_label, name_label, subtitle):
                bind_hover(hover_widget, on_enter, on_leave)

    def open_category(self, category_id, category_name, category_icon):
        self.current_category_id = category_id
        self.current_category_name = category_name
        self.current_category_icon = category_icon
        self.clear_page()

        header = self.page_title(
            self,
            f"{category_icon} {category_name}",
            "ط£ظ†ط´ط¦ ط¨ط·ط§ظ‚ط© ظ„ظƒظ„ ظ†ظ…ظˆط°ط¬. ظƒظ„ ط¨ط·ط§ظ‚ط© ظ„ظ‡ط§ ط§ط³طھظ…ط§ط±ط© ط®ط§طµط© ظˆظ…ظ„ظپ ظˆظˆط±ط¯ ط£ظˆ ظ…ط­ط±ط± ط¯ط§ط®ظ„ظٹ."
        )

        back_btn = ctk.CTkButton(header, text="â†© ط±ط¬ظˆط¹", width=110, height=38, fg_color="#6B7280", hover_color="#4B5563", command=self.build_categories_ui)
        back_btn.pack(side="left", padx=5, pady=5)

        toolbar = ctk.CTkFrame(self, fg_color=CARD, corner_radius=20, border_width=1, border_color=BORDER)
        toolbar.pack(fill="x", pady=(0, 16))

        add_btn = ctk.CTkButton(
            toolbar,
            text="â‍• ط¥ط¶ط§ظپط© ظ†ظ…ظˆط°ط¬ ط¬ط¯ظٹط¯",
            width=190,
            height=42,
            corner_radius=14,
            font=("Segoe UI", 14, "bold"),
            command=lambda: self.open_template_editor(),
        )
        add_btn.pack(side="right", padx=16, pady=14)

        self.template_search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="ط¨ط­ط« ظپظٹ ظ†ظ…ط§ط°ط¬ ظ‡ط°ط§ ط§ظ„ظ‚ط³ظ…...",
            height=42,
            width=320,
            corner_radius=14,
            font=("Segoe UI", 14),
        )
        self.template_search_entry.pack(side="left", padx=16, pady=14)
        self.template_search_entry.bind("<KeyRelease>", self.on_template_search_key)

        # طµظ†ط¯ظˆظ‚ ط§ظ„ط§ظ‚طھط±ط§ط­ط§طھ ظ„ط§ ظ†ط¹ط±ط¶ظ‡ ظˆظ‡ظˆ ظپط§ط±ط؛طŒ ظ„ط£ظ† CTkFrame ظٹظ…ظ„ظƒ ط§ط±طھظپط§ط¹ظ‹ط§ ط§ظپطھط±ط§ط¶ظٹظ‹ط§ ظٹط®ظ„ظ‚ ظپط±ط§ط؛ظ‹ط§ ظƒط¨ظٹط±ظ‹ط§.
        self.template_suggestions_area = ctk.CTkFrame(self, fg_color="transparent", height=1)

        # ظ…ظ†ط·ظ‚ط© ط§ظ„ط¨ط·ط§ظ‚ط§طھ: ط¥ط·ط§ط± ط¹ط§ط¯ظٹ ظ…ط«ط¨طھ ظپظٹ ط§ظ„ط£ط¹ظ„ظ‰.
        # ظ„ط§ ظ†ط³طھط¹ظ…ظ„ CTkScrollableFrame ظ‡ظ†ط§ ظ„ط£ظ†ظ‡ ظƒط§ظ† ظٹط¯ظپط¹ ط§ظ„ط¨ط·ط§ظ‚ط§طھ ظ„ظ„ط£ط³ظپظ„ ظˆظٹط¬ط¹ظ„ظ‡ط§ طھط®طھظپظٹ ط®ظ„ظپ ط­ط§ط¬ط² ط£ط¨ظٹط¶.
        self.templates_area = ctk.CTkFrame(self, fg_color="transparent")
        self.templates_area.pack(fill="x", expand=False, anchor="n", pady=(0, 0))
        self.load_templates_cards()


    def on_template_search_key(self, event=None):
        self.load_template_search_suggestions()
        self.load_templates_cards()

    def load_template_search_suggestions(self):
        if not self.template_suggestions_area or not self.template_search_entry:
            return
        for widget in self.template_suggestions_area.winfo_children():
            widget.destroy()
        self.template_suggestions_area.pack_forget()
        keyword = self.template_search_entry.get().strip()
        if not keyword:
            return
        try:
            templates = search_templates(self.current_category_id, keyword)[:6]
        except Exception:
            templates = []
        if not templates:
            return
        try:
            self.template_suggestions_area.pack(fill="x", pady=(0, 6), before=self.templates_area)
        except Exception:
            self.template_suggestions_area.pack(fill="x", pady=(0, 6))
        box = ctk.CTkFrame(self.template_suggestions_area, fg_color="#FFFFFF", corner_radius=14, border_width=1, border_color=BORDER)
        box.pack(fill="x", padx=6)
        for template_id, name, template_path, created_at, updated_at, template_content in templates:
            status = "ظˆظˆط±ط¯" if template_path else "ط¯ط§ط®ظ„ظٹ"
            btn = ctk.CTkButton(
                box,
                text=f"{name}  آ·  {status}",
                anchor="e",
                height=32,
                corner_radius=10,
                fg_color="transparent",
                hover_color="#EFF6FF",
                text_color=TEXT,
                font=("Segoe UI", 13),
                command=lambda value=name: self.choose_template_suggestion(value),
            )
            btn.pack(fill="x", padx=8, pady=3)

    def choose_template_suggestion(self, value):
        self.template_search_entry.delete(0, "end")
        self.template_search_entry.insert(0, value)
        if self.template_suggestions_area:
            for widget in self.template_suggestions_area.winfo_children():
                widget.destroy()
            self.template_suggestions_area.pack_forget()
        self.load_templates_cards()

    def load_templates_cards(self):
        if not self.templates_area:
            return
        for widget in self.templates_area.winfo_children():
            widget.destroy()

        keyword = self.template_search_entry.get().strip() if self.template_search_entry else ""
        try:
            templates = search_templates(self.current_category_id, keyword)
        except Exception as e:
            messagebox.showerror("ط®ط·ط£", f"طھط¹ط°ط± طھط­ظ…ظٹظ„ ط§ظ„ظ†ظ…ط§ط°ط¬:\n{e}")
            templates = []

        if not templates:
            empty = ctk.CTkFrame(self.templates_area, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
            empty.pack(fill="x", padx=0, pady=(8, 0), anchor="n")
            ctk.CTkLabel(empty, text="ظ„ط§ طھظˆط¬ط¯ ظ†ظ…ط§ط°ط¬ ظ…ط·ط§ط¨ظ‚ط©.", font=("Segoe UI", 18, "bold"), text_color=TEXT).pack(pady=(22, 6))
            ctk.CTkLabel(empty, text="ط§ط¶ط؛ط· ط¹ظ„ظ‰ ط¥ط¶ط§ظپط© ظ†ظ…ظˆط°ط¬ ط¬ط¯ظٹط¯ ظ„ط¥ظ†ط´ط§ط، ط§ط³طھظ…ط§ط±ط© ظˆظ‚ط§ظ„ط¨ ط®ط§طµ ط¨ظ‡ط§.", font=("Segoe UI", 13), text_color=MUTED).pack(pady=(0, 22))
            return

        grid = ctk.CTkFrame(self.templates_area, fg_color="transparent")
        grid.pack(fill="x", anchor="n", pady=(0, 0))
        for col in range(2):
            grid.grid_columnconfigure(col, weight=1, uniform="template_cards")

        for index, item in enumerate(templates):
            template_id, name, template_path, created_at, updated_at, template_content = item
            row, col = divmod(index, 2)
            self.template_card(grid, template_id, name, template_path, template_content, updated_at, row, col)

    def template_card(self, parent, template_id, name, template_path, template_content, updated_at, row, col):
        fields = get_template_fields(template_id)
        card = ctk.CTkFrame(parent, corner_radius=18, fg_color=CARD, border_width=1, border_color=BORDER)
        card.grid(row=row, column=col, sticky="ew", padx=10, pady=10)
        card.grid_propagate(False)
        card.configure(height=118)

        def open_form(_event=None):
            self.open_fill_form_window(template_id)

        def make_clickable(widget):
            try:
                widget.configure(cursor="hand2")
            except Exception:
                pass
            widget.bind("<Button-1>", open_form)

        # ط£ط²ط±ط§ط± طµط؛ظٹط±ط© ظپظٹ ط£ط¹ظ„ظ‰ ط§ظ„ط¨ط·ط§ظ‚ط©طŒ ظ„ط§ طھط¯ظپط¹ ط§ظ„ظ…ط­طھظˆظ‰ ظ„ظ„ط£ط³ظپظ„.
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(8, 0))

        delete_btn = ctk.CTkButton(
            top, text="ًں—‘ï¸ڈ", width=32, height=28, corner_radius=9,
            fg_color="#FEE2E2", hover_color="#FECACA", text_color="#991B1B",
            font=("Segoe UI Emoji", 13), command=lambda: self.confirm_delete_template(template_id),
        )
        delete_btn.pack(side="left", padx=(0, 4))

        edit_btn = ctk.CTkButton(
            top, text="âœڈï¸ڈ", width=32, height=28, corner_radius=9,
            fg_color="#FEF3C7", hover_color="#FDE68A", text_color="#92400E",
            font=("Segoe UI Emoji", 13), command=lambda: self.open_template_editor(template_id),
        )
        edit_btn.pack(side="left", padx=(0, 4))

        icon_label = ctk.CTkLabel(top, text="ًں“„", font=("Segoe UI Emoji", 22), text_color=TEXT)
        icon_label.pack(side="right", padx=(6, 0))
        make_clickable(icon_label)

        title_label = ctk.CTkLabel(top, text=name, font=("Segoe UI", 16, "bold"), text_color=TEXT, anchor="e")
        title_label.pack(side="right", fill="x", expand=True)
        make_clickable(title_label)

        status_text = "ظ‚ط§ظ„ط¨ ظˆظˆط±ط¯" if template_path else "ظ‚ط§ظ„ط¨ ط¯ط§ط®ظ„ظٹ" if template_content else "ط¨ط¯ظˆظ† ظ‚ط§ظ„ط¨"
        info_label = ctk.CTkLabel(card, text=f"{status_text}  â€¢  {len(fields)} ط®ط§ظ†ط§طھ", font=("Segoe UI", 11), text_color=MUTED, anchor="e")
        info_label.pack(fill="x", padx=16, pady=(8, 0))
        make_clickable(info_label)

        date_label = ctk.CTkLabel(card, text=f"ط¢ط®ط± طھط¹ط¯ظٹظ„: {updated_at}", font=("Segoe UI", 10), text_color="#9CA3AF", anchor="e")
        date_label.pack(fill="x", padx=16, pady=(4, 0))
        make_clickable(date_label)

        make_clickable(card)

        def enter(_event=None):
            card.configure(fg_color="#EFF6FF", border_color=BLUE)
            icon_label.configure(text_color=BLUE)
            title_label.configure(text_color=BLUE)

        def leave(_event=None):
            card.configure(fg_color=CARD, border_color=BORDER)
            icon_label.configure(text_color=TEXT)
            title_label.configure(text_color=TEXT)

        for widget in (card, icon_label, title_label, info_label, date_label):
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)


    def make_modal(self, title, size="900x760"):
        window = ctk.CTkToplevel(self)
        window.title(title)
        window.geometry(size)
        window.transient(self.winfo_toplevel())
        window.focus_force()
        window.grab_set()
        return window

    def open_template_editor(self, template_id=None):
        try:
            self._open_template_editor(template_id)
        except Exception as e:
            messagebox.showerror("ط®ط·ط£", f"طھط¹ط°ط± ظپطھط­ ظ…ط­ط±ط± ط§ظ„ظ†ظ…ظˆط°ط¬:\n{e}")

    def _open_template_editor(self, template_id=None):
        is_edit = template_id is not None
        existing = get_template(template_id) if is_edit else None
        existing_fields = get_template_fields(template_id) if is_edit else []

        selected_template_path = ctk.StringVar(value=existing[3] if existing and existing[3] else "")
        fields_list = [row[1] for row in existing_fields]

        window = self.make_modal("طھط¹ط¯ظٹظ„ ظ†ظ…ظˆط°ط¬" if is_edit else "ط¥ط¶ط§ظپط© ظ†ظ…ظˆط°ط¬ ط¬ط¯ظٹط¯", "920x790")
        container = ctk.CTkScrollableFrame(window, fg_color=BG)
        container.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(container, text=("طھط¹ط¯ظٹظ„ ظ†ظ…ظˆط°ط¬" if is_edit else f"ط¥ط¶ط§ظپط© ظ†ظ…ظˆط°ط¬ ط¯ط§ط®ظ„: {self.current_category_name}"), font=("Segoe UI", 25, "bold"), text_color=TEXT).pack(anchor="e", pady=(8, 18))

        card = ctk.CTkFrame(container, fg_color=CARD, corner_radius=22, border_width=1, border_color=BORDER)
        card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(card, text="ط§ط³ظ… ط§ظ„ظ†ظ…ظˆط°ط¬", font=("Segoe UI", 15, "bold"), text_color=TEXT, anchor="e").pack(fill="x", padx=18, pady=(18, 6))
        name_entry = ctk.CTkEntry(card, height=42, font=("Segoe UI", 15), placeholder_text="ظ…ط«ط§ظ„: ط·ظ„ط¨ ظˆط¸ظٹظپط©")
        name_entry.pack(fill="x", padx=18, pady=(0, 16))
        if existing:
            name_entry.insert(0, existing[2])

        fields_card = ctk.CTkFrame(container, fg_color=CARD, corner_radius=22, border_width=1, border_color=BORDER)
        fields_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(fields_card, text="ط®ط§ظ†ط§طھ ط§ظ„ط§ط³طھظ…ط§ط±ط©", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(anchor="e", padx=18, pady=(18, 8))

        input_row = ctk.CTkFrame(fields_card, fg_color="transparent")
        input_row.pack(fill="x", padx=18)
        field_entry = ctk.CTkEntry(input_row, height=40, placeholder_text="ط§ظƒطھط¨ ط§ط³ظ… ط§ظ„ط®ط§ظ†ط© ط«ظ… ط§ط¶ط؛ط· ط¥ط¶ط§ظپط©", font=("Segoe UI", 14))
        field_entry.pack(side="right", fill="x", expand=True, padx=(0, 8))

        fields_box = ctk.CTkTextbox(fields_card, height=160, font=("Segoe UI", 15))
        fields_box.pack(fill="x", padx=18, pady=12)

        def refresh_fields_box():
            fields_box.configure(state="normal")
            fields_box.delete("1.0", "end")
            if not fields_list:
                fields_box.insert("end", "ظ„ظ… طھط¶ظپ ط£ظٹ ط®ط§ظ†ط© ط¨ط¹ط¯.\n")
            else:
                for index, field in enumerate(fields_list, start=1):
                    key = make_field_key(field)
                    fields_box.insert("end", f"{index}. {field}     â†گ     {{{{{key}}}}}\n")
            fields_box.configure(state="disabled")

        def add_field(value=None):
            value = (value or field_entry.get()).strip()
            if not value:
                return
            if make_field_key(value) in [make_field_key(x) for x in fields_list]:
                messagebox.showwarning("طھظ†ط¨ظٹظ‡", "ظ‡ط°ظ‡ ط§ظ„ط®ط§ظ†ط© ظ…ظˆط¬ظˆط¯ط© ظ…ط³ط¨ظ‚ط§")
                return
            fields_list.append(value)
            field_entry.delete(0, "end")
            refresh_fields_box()

        def remove_last_field():
            if fields_list:
                fields_list.pop()
                refresh_fields_box()

        ctk.CTkButton(input_row, text="ط¥ط¶ط§ظپط©", width=120, height=40, command=add_field).pack(side="left")
        field_entry.bind("<Return>", lambda e: add_field())

        quick = ctk.CTkFrame(fields_card, fg_color="transparent")
        quick.pack(fill="x", padx=18, pady=(0, 8))
        for f in DEFAULT_FIELDS[:8]:
            ctk.CTkButton(quick, text=f"+ {f}", width=95, height=30, fg_color=GRAY_BTN, hover_color="#E5E7EB", text_color=TEXT, command=lambda x=f: add_field(x)).pack(side="right", padx=3, pady=3)

        ctk.CTkButton(fields_card, text="ط­ط°ظپ ط¢ط®ط± ط®ط§ظ†ط©", width=150, height=34, fg_color="#6B7280", hover_color="#4B5563", command=remove_last_field).pack(anchor="e", padx=18, pady=(0, 16))
        refresh_fields_box()

        template_card = ctk.CTkFrame(container, fg_color=CARD, corner_radius=22, border_width=1, border_color=BORDER)
        template_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(template_card, text="ط§ظ„ظ‚ط§ظ„ط¨", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(anchor="e", padx=18, pady=(18, 6))

        path_label = ctk.CTkLabel(template_card, text=selected_template_path.get() or "ظ„ظ… ظٹطھظ… ط§ط®طھظٹط§ط± ظ…ظ„ظپ ظˆظˆط±ط¯ ط¨ط¹ط¯", font=("Segoe UI", 13), text_color=MUTED, wraplength=780, justify="right")
        path_label.pack(fill="x", padx=18, pady=(0, 8))

        def choose_word_template():
            file_path = filedialog.askopenfilename(title="ط§ط®طھط± ظ†ظ…ظˆط°ط¬ ظˆظˆط±ط¯", filetypes=[("ظ…ظ„ظپط§طھ ظˆظˆط±ط¯", "*.docx"), ("ظƒظ„ ط§ظ„ظ…ظ„ظپط§طھ", "*.*")])
            if file_path:
                selected_template_path.set(file_path)
                path_label.configure(text=file_path)

        def clear_word_template():
            selected_template_path.set("")
            path_label.configure(text="ظ„ظ… ظٹطھظ… ط§ط®طھظٹط§ط± ظ…ظ„ظپ ظˆظˆط±ط¯ ط¨ط¹ط¯")

        btns = ctk.CTkFrame(template_card, fg_color="transparent")
        btns.pack(fill="x", padx=18, pady=(0, 14))
        ctk.CTkButton(btns, text="ًں“ژ ط±ظپط¹ ظ†ظ…ظˆط°ط¬ ظˆظˆط±ط¯ ظ…ظ† ط§ظ„ط¬ظ‡ط§ط²", height=40, command=choose_word_template).pack(side="right", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(btns, text="ط¥ط²ط§ظ„ط© ظ…ظ„ظپ ظˆظˆط±ط¯ ظˆط§ط³طھط¹ظ…ط§ظ„ ط§ظ„ظ…ط­ط±ط±", height=40, fg_color="#6B7280", hover_color="#4B5563", command=clear_word_template).pack(side="left", fill="x", expand=True, padx=(5, 0))

        ctk.CTkLabel(template_card, text="ط§ظ„ظ…ط­ط±ط± ط§ظ„ط¯ط§ط®ظ„ظٹ: ط§ط³طھط¹ظ…ظ„ ط§ظ„ط®ط§ظ†ط§طھ ط¨ط§ظ„ط´ظƒظ„ {{ط§ظ„ط§ط³ظ…}} ط£ظˆ {{ط±ظ‚ظ…_ط§ظ„ظ‡ط§طھظپ}}", font=("Segoe UI", 13), text_color=MUTED).pack(anchor="e", padx=18)
        editor = ctk.CTkTextbox(template_card, height=250, font=("Segoe UI", 15))
        editor.pack(fill="x", padx=18, pady=(8, 18))
        if existing and existing[6]:
            editor.insert("end", existing[6])
        else:
            editor.insert("end", "ط§ظƒطھط¨ ظ†طµ ط§ظ„ظ†ظ…ظˆط°ط¬ ظ‡ظ†ط§...\n\nط£ظ†ط§ ط§ظ„ظ…ظ…ط¶ظٹ ط£ط³ظپظ„ظ‡ {{ط§ظ„ط§ط³ظ…}} {{ط§ظ„ظ„ظ‚ط¨}}\nط§ظ„ط³ط§ظƒظ† ط¨ظ€ {{ط§ظ„ط¹ظ†ظˆط§ظ†}}\nط±ظ‚ظ… ط§ظ„ظ‡ط§طھظپ: {{ط±ظ‚ظ…_ط§ظ„ظ‡ط§طھظپ}}\n")

        def save_template_action():
            template_name = name_entry.get().strip()
            if not template_name:
                messagebox.showerror("ط®ط·ط£", "ط§ظƒطھط¨ ط§ط³ظ… ط§ظ„ظ†ظ…ظˆط°ط¬")
                return
            if not fields_list:
                messagebox.showerror("ط®ط·ط£", "ط£ط¶ظپ ط®ط§ظ†ط§طھ ط§ظ„ط§ط³طھظ…ط§ط±ط©")
                return

            source_path = selected_template_path.get().strip()
            final_path = existing[3] if existing and existing[3] else None
            template_content = editor.get("1.0", "end").strip()

            if source_path:
                if os.path.exists(source_path) and os.path.abspath(source_path) != os.path.abspath(final_path or ""):
                    final_path = os.path.join(TEMPLATES_FOLDER, f"{safe_template_file_name(template_name)}_{template_id or 'new'}.docx")
                    try:
                        shutil.copy2(source_path, final_path)
                    except Exception as e:
                        messagebox.showerror("ط®ط·ط£", f"طھط¹ط°ط± ظ†ط³ط® ظ…ظ„ظپ ظˆظˆط±ط¯:\n{e}")
                        return
                template_content_to_save = None
            else:
                final_path = None
                template_content_to_save = template_content

            if not final_path and not template_content_to_save:
                messagebox.showerror("ط®ط·ط£", "ط§ط±ظپط¹ ظ…ظ„ظپ ظˆظˆط±ط¯ ط£ظˆ ط§ظƒطھط¨ ط§ظ„ظ†ظ…ظˆط°ط¬ ط¯ط§ط®ظ„ ط§ظ„ظ…ط­ط±ط±")
                return

            try:
                if is_edit:
                    update_template(template_id, template_name, fields_list, final_path, template_content_to_save)
                else:
                    new_id = add_template(self.current_category_id, template_name, fields_list, final_path, template_content_to_save)
                    if final_path and final_path.endswith("_new.docx"):
                        pass
                messagebox.showinfo("طھظ…", "طھظ… ط­ظپط¸ ط§ظ„ظ†ظ…ظˆط°ط¬ ط¨ظ†ط¬ط§ط­")
                window.destroy()
                self.load_templates_cards()
            except Exception as e:
                messagebox.showerror("ط®ط·ط£", f"طھط¹ط°ط± ط­ظپط¸ ط§ظ„ظ†ظ…ظˆط°ط¬:\n{e}")

        ctk.CTkButton(container, text="ًں’¾ ط­ظپط¸ ط§ظ„ظ†ظ…ظˆط°ط¬", height=48, corner_radius=16, font=("Segoe UI", 16, "bold"), command=save_template_action).pack(fill="x", pady=(0, 20))

    def open_fill_form_window(self, template_id):
        try:
            self._open_fill_form_window(template_id)
        except Exception as e:
            messagebox.showerror("ط®ط·ط£ ظپظٹ ظپطھط­ ط§ظ„ط§ط³طھظ…ط§ط±ط©", str(e))

    def _open_fill_form_window(self, template_id):
        template = get_template(template_id)
        fields = get_template_fields(template_id)
        if not template:
            messagebox.showerror("ط®ط·ط£", "ط§ظ„ظ†ظ…ظˆط°ط¬ ط؛ظٹط± ظ…ظˆط¬ظˆط¯")
            return

        template_name = template[2]
        template_path = template[3]
        template_content = template[6] if len(template) > 6 else None
        entries = {}

        window = self.make_modal(template_name, "820x790")
        container = ctk.CTkScrollableFrame(window, fg_color=BG)
        container.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(container, text=f"ط§ط³طھظ…ط§ط±ط©: {template_name}", font=("Segoe UI", 25, "bold"), text_color=TEXT).pack(anchor="e", pady=(8, 6))
        ctk.CTkLabel(container, text="ط§ظ…ظ„ط£ ط¨ظٹط§ظ†ط§طھ ط§ظ„ط²ط¨ظˆظ† ط«ظ… ط£ظ†ط´ط¦ ط§ظ„ظˆط«ظٹظ‚ط©. ط³ظٹطھظ… ط­ظپط¸ ط§ظ„ط²ط¨ظˆظ† ظˆط§ظ„ط£ط±ط´ظٹظپ طھظ„ظ‚ط§ط¦ظٹط§.", font=("Segoe UI", 14), text_color=MUTED).pack(anchor="e", pady=(0, 14))

        customers = search_customers("")[:80]
        customer_map = {}
        customer_values = ["-- ط§ط®طھط± ط²ط¨ظˆظ†ط§ ظ…ط­ظپظˆط¸ط§ --"]
        for cid, first, last, address, phone in customers:
            label = f"{first or ''} {last or ''} | {phone or ''}".strip()
            customer_values.append(label)
            customer_map[label] = {"ط§ظ„ط§ط³ظ…": first or "", "ط§ظ„ظ„ظ‚ط¨": last or "", "ط§ظ„ط¹ظ†ظˆط§ظ†": address or "", "ط±ظ‚ظ…_ط§ظ„ظ‡ط§طھظپ": phone or "", "ط§ظ„ظ‡ط§طھظپ": phone or ""}

        if customers:
            choose_card = ctk.CTkFrame(container, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
            choose_card.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(choose_card, text="ط§ط®طھظٹط§ط± ط²ط¨ظˆظ† ظ…ط­ظپظˆط¸", font=("Segoe UI", 14, "bold"), text_color=TEXT).pack(anchor="e", padx=16, pady=(14, 6))
            combo = ctk.CTkComboBox(choose_card, values=customer_values, height=38, font=("Segoe UI", 13))
            combo.pack(fill="x", padx=16, pady=(0, 14))

            def fill_customer(choice):
                data = customer_map.get(choice)
                if not data:
                    return
                for key, value in data.items():
                    if key in entries and value:
                        entries[key].delete(0, "end")
                        entries[key].insert(0, value)
            combo.configure(command=fill_customer)

        form_card = ctk.CTkFrame(container, fg_color=CARD, corner_radius=22, border_width=1, border_color=BORDER)
        form_card.pack(fill="x", pady=(0, 14))

        for field_id, field_label, field_key, field_order in fields:
            ctk.CTkLabel(form_card, text=field_label, font=("Segoe UI", 14, "bold"), text_color=TEXT, anchor="e").pack(fill="x", padx=18, pady=(13, 5))
            entry = ctk.CTkEntry(form_card, height=40, font=("Segoe UI", 14), placeholder_text=field_label)
            entry.pack(fill="x", padx=18)
            entries[field_key] = entry
        ctk.CTkFrame(form_card, fg_color="transparent", height=10).pack()

        def collect_data():
            data = {}
            for field_id, field_label, field_key, field_order in fields:
                data[field_key] = entries[field_key].get().strip()
            return data

        def get_value(data, labels):
            for label in labels:
                key = make_field_key(label)
                if data.get(key):
                    return data[key]
            return ""

        def save_customer_from_form(data):
            first_name = get_value(data, ["ط§ظ„ط§ط³ظ…", "ط§ظ„ط¥ط³ظ…", "ط§ط³ظ…"])
            last_name = get_value(data, ["ط§ظ„ظ„ظ‚ط¨"])
            address = get_value(data, ["ط§ظ„ط¹ظ†ظˆط§ظ†", "ط§ظ„ط§ظ‚ط§ظ…ط©", "ط§ظ„ط¥ظ‚ط§ظ…ط©", "ظ…ظƒط§ظ† ط§ظ„ط¥ظ‚ط§ظ…ط©"])
            phone = get_value(data, ["ط§ظ„ظ‡ط§طھظپ", "ط±ظ‚ظ… ط§ظ„ظ‡ط§طھظپ", "ط±ظ‚ظ…_ط§ظ„ظ‡ط§طھظپ", "ط§ظ„ط±ظ‚ظ…"])
            if first_name or last_name or phone:
                save_customer(first_name, last_name, address, phone)
            return first_name, last_name, address, phone

        def preview_data():
            data = collect_data()
            preview = self.make_modal("ظ…ط¹ط§ظٹظ†ط©", "760x650")
            box = ctk.CTkFrame(preview, fg_color=BG)
            box.pack(fill="both", expand=True, padx=18, pady=18)
            ctk.CTkLabel(box, text="ظ…ط¹ط§ظٹظ†ط© ظ‚ط¨ظ„ ط¥ظ†ط´ط§ط، ط§ظ„ظˆط«ظٹظ‚ط©", font=("Segoe UI", 22, "bold"), text_color=TEXT).pack(anchor="e", pady=(0, 12))
            text = ctk.CTkTextbox(box, font=("Segoe UI", 15))
            text.pack(fill="both", expand=True)
            if template_content:
                text.insert("end", render_text_template(template_content, data))
            else:
                text.insert("end", f"ط§ظ„ظ†ظ…ظˆط°ط¬: {template_name}\nط§ظ„ظ‚ط³ظ…: {self.current_category_name}\n\n")
                for field_id, field_label, field_key, field_order in fields:
                    text.insert("end", f"{field_label}: {data.get(field_key, '')}\n")
            text.configure(state="disabled")

        def create_document():
            data = collect_data()
            if not template_path and not template_content:
                messagebox.showerror("ط®ط·ط£", "ظ‡ط°ط§ ط§ظ„ظ†ظ…ظˆط°ط¬ ط؛ظٹط± ظ…ط±طھط¨ط· ط¨ظ…ظ„ظپ ظˆظˆط±ط¯ ظˆظ„ط§ ظٹط­طھظˆظٹ ط¹ظ„ظ‰ ظ†طµ ط¯ط§ط®ظ„ظٹ.")
                return
            try:
                if template_path:
                    output_path = generate_word_document(template_path, data, template_name)
                else:
                    output_path = generate_word_from_text_template(template_content, data, template_name)

                pdf_path = ""
                pdf_error = ""
                try:
                    pdf_path = convert_word_to_pdf(output_path)
                except Exception as pdf_exc:
                    pdf_error = str(pdf_exc)

                first_name, last_name, address, phone = save_customer_from_form(data)
                customer_name = f"{first_name} {last_name}".strip()
                save_archive(customer_name, phone, self.current_category_name, template_name, output_path, pdf_path)
                self.show_result_window(window, output_path, pdf_path, pdf_error)
            except Exception as e:
                messagebox.showerror("ط®ط·ط£", f"طھط¹ط°ط± ط¥ظ†ط´ط§ط، ط§ظ„ظˆط«ظٹظ‚ط©:\n{e}")

        buttons = ctk.CTkFrame(container, fg_color="transparent")
        buttons.pack(fill="x", pady=(4, 18))
        ctk.CTkButton(buttons, text="ًں‘پ ظ…ط¹ط§ظٹظ†ط©", height=46, corner_radius=15, font=("Segoe UI", 15, "bold"), fg_color="#6B7280", hover_color="#4B5563", command=preview_data).pack(side="right", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(buttons, text="ًں“„ ط¥ظ†ط´ط§ط، ظˆظˆط±ط¯ ظˆط¨ظٹ ط¯ظٹ ط¥ظپ", height=46, corner_radius=15, font=("Segoe UI", 15, "bold"), fg_color=GREEN, hover_color="#047857", command=create_document).pack(side="left", fill="x", expand=True, padx=(6, 0))

    def show_result_window(self, parent, output_path, pdf_path, pdf_error=""):
        result = self.make_modal("طھظ… ط¥ظ†ط´ط§ط، ط§ظ„ظˆط«ظٹظ‚ط©", "680x400")
        box = ctk.CTkFrame(result, fg_color=BG)
        box.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(box, text="âœ… طھظ… ط¥ظ†ط´ط§ط، ط§ظ„ظˆط«ظٹظ‚ط© ظˆط­ظپط¸ظ‡ط§ ظپظٹ ط§ظ„ط£ط±ط´ظٹظپ", font=("Segoe UI", 22, "bold"), text_color=TEXT).pack(pady=(8, 14))
        path_text = ctk.CTkTextbox(box, height=105, font=("Segoe UI", 13))
        path_text.pack(fill="x", pady=8)
        if pdf_path:
            path_text.insert("end", f"Word:\n{output_path}\n\nPDF:\n{pdf_path}")
        else:
            path_text.insert("end", f"Word:\n{output_path}\n\nPDF:\nظ„ظ… ظٹطھظ… ط¥ظ†ط´ط§ط، PDF.\n\nط§ظ„ط³ط¨ط¨:\n{pdf_error}")
        path_text.configure(state="disabled")
        buttons = ctk.CTkFrame(box, fg_color="transparent")
        buttons.pack(fill="x", pady=(18, 0))
        ctk.CTkButton(buttons, text="ًں“„ ظپطھط­ ظ…ظ„ظپ ظˆظˆط±ط¯", height=40, command=lambda: open_file(output_path)).pack(side="right", fill="x", expand=True, padx=5)
        if pdf_path:
            ctk.CTkButton(buttons, text="ًں“• ظپطھط­ PDF", height=40, command=lambda: open_file(pdf_path)).pack(side="right", fill="x", expand=True, padx=5)
            ctk.CTkButton(buttons, text="ًں–¨ï¸ڈ ط·ط¨ط§ط¹ط© PDF", height=40, fg_color=GREEN, hover_color="#047857", command=lambda: print_file(pdf_path)).pack(side="right", fill="x", expand=True, padx=5)
        else:
            ctk.CTkButton(buttons, text="ًں“• ظ„ظ… ظٹطھظ… ط¥ظ†ط´ط§ط، PDF", height=40, state="disabled").pack(side="right", fill="x", expand=True, padx=5)

    def confirm_delete_template(self, template_id):
        answer = messagebox.askyesno("طھط£ظƒظٹط¯ ط§ظ„ط­ط°ظپ", "ظ‡ظ„ طھط±ظٹط¯ ط­ط°ظپ ظ‡ط°ط§ ط§ظ„ظ†ظ…ظˆط°ط¬طں\nط³ظٹطھظ… ط­ط°ظپ ط§ظ„ط§ط³طھظ…ط§ط±ط© ظˆط±ط¨ط·ظ‡ط§ ط¨ط§ظ„ظ‚ط§ظ„ط¨طŒ ظ„ظƒظ† ط§ظ„ظˆط«ط§ط¦ظ‚ ط§ظ„ظ‚ط¯ظٹظ…ط© ظپظٹ ط§ظ„ط£ط±ط´ظٹظپ ظ„ط§ طھط­ط°ظپ.")
        if answer:
            try:
                delete_template(template_id)
                self.load_templates_cards()
            except Exception as e:
                messagebox.showerror("ط®ط·ط£", f"طھط¹ط°ط± ط­ط°ظپ ط§ظ„ظ†ظ…ظˆط°ط¬:\n{e}")
