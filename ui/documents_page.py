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
    "الاسم", "اللقب", "تاريخ الميلاد", "العنوان", "رقم الهاتف", "تاريخ الطلب",
    "الجهة المرسل إليها", "المنصب", "الشهادة", "التخصص", "المستوى الدراسي", "الخبرة",
    "الجامعة", "ولاية الجامعة", "السنة الجامعية", "الدفعة",
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
            "📄 قسم الوثائق",
            "اختر القسم، ثم أنشئ نماذج وورد واستمارات خاصة بكل وثيقة."
        )

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, pady=(15, 0))

        try:
            categories = get_categories()
        except Exception as e:
            messagebox.showerror("خطأ", f"تعذر تحميل الأقسام:\n{e}")
            categories = []

        for col in range(4):
            grid.grid_columnconfigure(col, weight=1, uniform="document_categories")

        visible_categories = [cat for cat in categories if cat[1] != "أخرى"]

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

            subtitle = ctk.CTkLabel(card, text="إدارة النماذج والاستمارات", font=("Segoe UI", 12), text_color=MUTED)
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
            "أنشئ بطاقة لكل نموذج. كل بطاقة لها استمارة خاصة وملف وورد أو محرر داخلي."
        )

        back_btn = ctk.CTkButton(header, text="↩ رجوع", width=110, height=38, fg_color="#6B7280", hover_color="#4B5563", command=self.build_categories_ui)
        back_btn.pack(side="left", padx=5, pady=5)

        toolbar = ctk.CTkFrame(self, fg_color=CARD, corner_radius=20, border_width=1, border_color=BORDER)
        toolbar.pack(fill="x", pady=(0, 16))

        add_btn = ctk.CTkButton(
            toolbar,
            text="➕ إضافة نموذج جديد",
            width=190,
            height=42,
            corner_radius=14,
            font=("Segoe UI", 14, "bold"),
            command=lambda: self.open_template_editor(),
        )
        add_btn.pack(side="right", padx=16, pady=14)

        self.template_search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="بحث في نماذج هذا القسم...",
            height=42,
            width=320,
            corner_radius=14,
            font=("Segoe UI", 14),
        )
        self.template_search_entry.pack(side="left", padx=16, pady=14)
        self.template_search_entry.bind("<KeyRelease>", self.on_template_search_key)

        self.template_suggestions_area = None

        self.templates_area = ctk.CTkFrame(self, fg_color="transparent")
        self.templates_area.pack(fill="x", expand=False, anchor="n", pady=(0, 0))
        self.load_templates_cards()

    def on_template_search_key(self, event=None):
        self.load_template_search_suggestions()
        self.load_templates_cards()

    def load_template_search_suggestions(self):
        if not self.template_search_entry:
            return
        if self.template_suggestions_area:
            self.template_suggestions_area.destroy()
            self.template_suggestions_area = None
        keyword = self.template_search_entry.get().strip()
        if not keyword:
            return
        try:
            templates = search_templates(self.current_category_id, keyword)[:6]
        except Exception:
            templates = []
        if not templates:
            return
        self.template_suggestions_area = ctk.CTkFrame(self, fg_color="transparent")
        self.template_suggestions_area.pack(fill="x", pady=(0, 6), before=self.templates_area)
        box = ctk.CTkFrame(self.template_suggestions_area, fg_color="#FFFFFF", corner_radius=14, border_width=1, border_color=BORDER)
        box.pack(fill="x", padx=6)
        for template_id, name, template_path, created_at, updated_at, template_content in templates:
            status = "وورد" if template_path else "داخلي"
            btn = ctk.CTkButton(
                box,
                text=f"{name}  ·  {status}",
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
            self.template_suggestions_area.destroy()
            self.template_suggestions_area = None
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
            messagebox.showerror("خطأ", f"تعذر تحميل النماذج:\n{e}")
            templates = []

        if not templates:
            empty = ctk.CTkFrame(self.templates_area, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
            empty.pack(fill="x", padx=0, pady=(8, 0), anchor="n")
            ctk.CTkLabel(empty, text="لا توجد نماذج مطابقة.", font=("Segoe UI", 18, "bold"), text_color=TEXT).pack(pady=(22, 6))
            ctk.CTkLabel(empty, text="اضغط على إضافة نموذج جديد لإنشاء استمارة وقالب خاص بها.", font=("Segoe UI", 13), text_color=MUTED).pack(pady=(0, 22))
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

        # أزرار صغيرة في أعلى البطاقة، لا تدفع المحتوى للأسفل.
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(8, 0))

        delete_btn = ctk.CTkButton(
            top, text="🗑️", width=32, height=28, corner_radius=9,
            fg_color="#FEE2E2", hover_color="#FECACA", text_color="#991B1B",
            font=("Segoe UI Emoji", 13), command=lambda: self.confirm_delete_template(template_id),
        )
        delete_btn.pack(side="left", padx=(0, 4))

        edit_btn = ctk.CTkButton(
            top, text="✏️", width=32, height=28, corner_radius=9,
            fg_color="#FEF3C7", hover_color="#FDE68A", text_color="#92400E",
            font=("Segoe UI Emoji", 13), command=lambda: self.open_template_editor(template_id),
        )
        edit_btn.pack(side="left", padx=(0, 4))

        icon_label = ctk.CTkLabel(top, text="📄", font=("Segoe UI Emoji", 22), text_color=TEXT)
        icon_label.pack(side="right", padx=(6, 0))
        make_clickable(icon_label)

        title_label = ctk.CTkLabel(top, text=name, font=("Segoe UI", 16, "bold"), text_color=TEXT, anchor="e")
        title_label.pack(side="right", fill="x", expand=True)
        make_clickable(title_label)

        status_text = "قالب وورد" if template_path else "قالب داخلي" if template_content else "بدون قالب"
        info_label = ctk.CTkLabel(card, text=f"{status_text}  •  {len(fields)} خانات", font=("Segoe UI", 11), text_color=MUTED, anchor="e")
        info_label.pack(fill="x", padx=16, pady=(8, 0))
        make_clickable(info_label)

        date_label = ctk.CTkLabel(card, text=f"آخر تعديل: {updated_at}", font=("Segoe UI", 10), text_color="#9CA3AF", anchor="e")
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
            messagebox.showerror("خطأ", f"تعذر فتح محرر النموذج:\n{e}")

    def _open_template_editor(self, template_id=None):
        is_edit = template_id is not None
        existing = get_template(template_id) if is_edit else None
        existing_fields = get_template_fields(template_id) if is_edit else []

        selected_template_path = ctk.StringVar(value=existing[3] if existing and existing[3] else "")
        fields_list = [row[1] for row in existing_fields]

        window = self.make_modal("تعديل نموذج" if is_edit else "إضافة نموذج جديد", "920x790")
        container = ctk.CTkScrollableFrame(window, fg_color=BG)
        container.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(container, text=("تعديل نموذج" if is_edit else f"إضافة نموذج داخل: {self.current_category_name}"), font=("Segoe UI", 25, "bold"), text_color=TEXT).pack(anchor="e", pady=(8, 18))

        card = ctk.CTkFrame(container, fg_color=CARD, corner_radius=22, border_width=1, border_color=BORDER)
        card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(card, text="اسم النموذج", font=("Segoe UI", 15, "bold"), text_color=TEXT, anchor="e").pack(fill="x", padx=18, pady=(18, 6))
        name_entry = ctk.CTkEntry(card, height=42, font=("Segoe UI", 15), placeholder_text="مثال: طلب وظيفة")
        name_entry.pack(fill="x", padx=18, pady=(0, 16))
        if existing:
            name_entry.insert(0, existing[2])

        fields_card = ctk.CTkFrame(container, fg_color=CARD, corner_radius=22, border_width=1, border_color=BORDER)
        fields_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(fields_card, text="خانات الاستمارة", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(anchor="e", padx=18, pady=(18, 8))

        input_row = ctk.CTkFrame(fields_card, fg_color="transparent")
        input_row.pack(fill="x", padx=18)
        field_entry = ctk.CTkEntry(input_row, height=40, placeholder_text="اكتب اسم الخانة ثم اضغط إضافة", font=("Segoe UI", 14))
        field_entry.pack(side="right", fill="x", expand=True, padx=(0, 8))

        fields_box = ctk.CTkTextbox(fields_card, height=160, font=("Segoe UI", 15))
        fields_box.pack(fill="x", padx=18, pady=12)

        def refresh_fields_box():
            fields_box.configure(state="normal")
            fields_box.delete("1.0", "end")
            if not fields_list:
                fields_box.insert("end", "لم تضف أي خانة بعد.\n")
            else:
                for index, field in enumerate(fields_list, start=1):
                    key = make_field_key(field)
                    fields_box.insert("end", f"{index}. {field}     ↢     {{{{{key}}}}}\n")
            fields_box.configure(state="disabled")

        def add_field(value=None):
            value = (value or field_entry.get()).strip()
            if not value:
                return
            if make_field_key(value) in [make_field_key(x) for x in fields_list]:
                messagebox.showwarning("تنبيه", "هذه الخانة موجودة مسبقا")
                return
            fields_list.append(value)
            field_entry.delete(0, "end")
            refresh_fields_box()

        def remove_last_field():
            if fields_list:
                fields_list.pop()
                refresh_fields_box()

        ctk.CTkButton(input_row, text="إضافة", width=120, height=40, command=add_field).pack(side="left")
        field_entry.bind("<Return>", lambda e: add_field())

        quick = ctk.CTkFrame(fields_card, fg_color="transparent")
        quick.pack(fill="x", padx=18, pady=(0, 8))
        for f in DEFAULT_FIELDS[:8]:
            ctk.CTkButton(quick, text=f"+ {f}", width=95, height=30, fg_color=GRAY_BTN, hover_color="#E5E7EB", text_color=TEXT, command=lambda x=f: add_field(x)).pack(side="right", padx=3, pady=3)

        ctk.CTkButton(fields_card, text="حذف آخر خانة", width=150, height=34, fg_color="#6B7280", hover_color="#4B5563", command=remove_last_field).pack(anchor="e", padx=18, pady=(0, 16))
        refresh_fields_box()

        template_card = ctk.CTkFrame(container, fg_color=CARD, corner_radius=22, border_width=1, border_color=BORDER)
        template_card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(template_card, text="القالب", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(anchor="e", padx=18, pady=(18, 6))

        path_label = ctk.CTkLabel(template_card, text=selected_template_path.get() or "لم يتم اختيار ملف وورد بعد", font=("Segoe UI", 13), text_color=MUTED, wraplength=780, justify="right")
        path_label.pack(fill="x", padx=18, pady=(0, 8))

        def choose_word_template():
            file_path = filedialog.askopenfilename(title="اختر نموذج وورد", filetypes=[("ملفات وورد", "*.docx"), ("كل الملفات", "*.*")])
            if file_path:
                selected_template_path.set(file_path)
                path_label.configure(text=file_path)

        def clear_word_template():
            selected_template_path.set("")
            path_label.configure(text="لم يتم اختيار ملف وورد بعد")

        btns = ctk.CTkFrame(template_card, fg_color="transparent")
        btns.pack(fill="x", padx=18, pady=(0, 14))
        ctk.CTkButton(btns, text="📎 رفع نموذج وورد من الجهاز", height=40, command=choose_word_template).pack(side="right", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(btns, text="إزالة ملف وورد واستعمال المحرر", height=40, fg_color="#6B7280", hover_color="#4B5563", command=clear_word_template).pack(side="left", fill="x", expand=True, padx=(5, 0))

        ctk.CTkLabel(template_card, text="المحرر الداخلي: استعمل الخانات بالشكل {{الاسم}} أو {{رقم_الهاتف}}", font=("Segoe UI", 13), text_color=MUTED).pack(anchor="e", padx=18)
        editor = ctk.CTkTextbox(template_card, height=250, font=("Segoe UI", 15))
        editor.pack(fill="x", padx=18, pady=(8, 18))
        if existing and existing[6]:
            editor.insert("end", existing[6])
        else:
            editor.insert("end", "اكتب نص النموذج هنا...\n\nأنا الممضي أسفله {{الاسم}} {{اللقب}}\nالساكن بـ {{العنوان}}\nرقم الهاتف: {{رقم_الهاتف}}\n")

        def save_template_action():
            template_name = name_entry.get().strip()
            if not template_name:
                messagebox.showerror("خطأ", "اكتب اسم النموذج")
                return
            if not fields_list:
                messagebox.showerror("خطأ", "أضف خانات الاستمارة")
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
                        messagebox.showerror("خطأ", f"تعذر نسخ ملف وورد:\n{e}")
                        return
                template_content_to_save = None
            else:
                final_path = None
                template_content_to_save = template_content

            if not final_path and not template_content_to_save:
                messagebox.showerror("خطأ", "ارفع ملف وورد أو اكتب النموذج داخل المحرر")
                return

            try:
                if is_edit:
                    update_template(template_id, template_name, fields_list, final_path, template_content_to_save)
                else:
                    new_id = add_template(self.current_category_id, template_name, fields_list, final_path, template_content_to_save)
                    if final_path and final_path.endswith("_new.docx"):
                        pass
                messagebox.showinfo("تم", "تم حفظ النموذج بنجاح")
                window.destroy()
                self.load_templates_cards()
            except Exception as e:
                messagebox.showerror("خطأ", f"تعذر حفظ النموذج:\n{e}")

        ctk.CTkButton(container, text="💾 حفظ النموذج", height=48, corner_radius=16, font=("Segoe UI", 16, "bold"), command=save_template_action).pack(fill="x", pady=(0, 20))

    def open_fill_form_window(self, template_id):
        try:
            self._open_fill_form_window(template_id)
        except Exception as e:
            messagebox.showerror("خطأ في فتح الاستمارة", str(e))

    def _open_fill_form_window(self, template_id):
        template = get_template(template_id)
        fields = get_template_fields(template_id)
        if not template:
            messagebox.showerror("خطأ", "النموذج غير موجود")
            return

        template_name = template[2]
        template_path = template[3]
        template_content = template[6] if len(template) > 6 else None
        entries = {}

        window = self.make_modal(template_name, "820x790")
        container = ctk.CTkScrollableFrame(window, fg_color=BG)
        container.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(container, text=f"استمارة: {template_name}", font=("Segoe UI", 25, "bold"), text_color=TEXT).pack(anchor="e", pady=(8, 6))
        ctk.CTkLabel(container, text="املأ بيانات الزبون ثم أنشئ الوثيقة. سيتم حفظ الزبون والأرشيف تلقائيا.", font=("Segoe UI", 14), text_color=MUTED).pack(anchor="e", pady=(0, 14))

        customers = search_customers("")[:80]
        customer_map = {}
        customer_values = ["-- اختر زبونا محفوظا --"]
        for cid, first, last, address, phone in customers:
            label = f"{first or ''} {last or ''} | {phone or ''}".strip()
            customer_values.append(label)
            customer_map[label] = {"الاسم": first or "", "اللقب": last or "", "العنوان": address or "", "رقم_الهاتف": phone or "", "الهاتف": phone or ""}

        if customers:
            choose_card = ctk.CTkFrame(container, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
            choose_card.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(choose_card, text="اختيار زبون محفوظ", font=("Segoe UI", 14, "bold"), text_color=TEXT).pack(anchor="e", padx=16, pady=(14, 6))
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
            first_name = get_value(data, ["الاسم", "الإسم", "اسم"])
            last_name = get_value(data, ["اللقب"])
            address = get_value(data, ["العنوان", "الاقامة", "الإقامة", "مكان الإقامة"])
            phone = get_value(data, ["الهاتف", "رقم الهاتف", "رقم_الهاتف", "الرقم"])
            if first_name or last_name or phone:
                save_customer(first_name, last_name, address, phone)
            return first_name, last_name, address, phone

        def preview_data():
            data = collect_data()
            preview = self.make_modal("معاينة", "760x650")
            box = ctk.CTkFrame(preview, fg_color=BG)
            box.pack(fill="both", expand=True, padx=18, pady=18)
            ctk.CTkLabel(box, text="معاينة قبل إنشاء الوثيقة", font=("Segoe UI", 22, "bold"), text_color=TEXT).pack(anchor="e", pady=(0, 12))
            text = ctk.CTkTextbox(box, font=("Segoe UI", 15))
            text.pack(fill="both", expand=True)
            if template_content:
                text.insert("end", render_text_template(template_content, data))
            else:
                text.insert("end", f"النموذج: {template_name}\nالقسم: {self.current_category_name}\n\n")
                for field_id, field_label, field_key, field_order in fields:
                    text.insert("end", f"{field_label}: {data.get(field_key, '')}\n")
            text.configure(state="disabled")

        def create_document():
            data = collect_data()
            if not template_path and not template_content:
                messagebox.showerror("خطأ", "هذا النموذج غير مرتبط بملف وورد ولا يحتوي على نص داخلي.")
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
                messagebox.showerror("خطأ", f"تعذر إنشاء الوثيقة:\n{e}")

        buttons = ctk.CTkFrame(container, fg_color="transparent")
        buttons.pack(fill="x", pady=(4, 18))
        ctk.CTkButton(buttons, text="👁 معاينة", height=46, corner_radius=15, font=("Segoe UI", 15, "bold"), fg_color="#6B7280", hover_color="#4B5563", command=preview_data).pack(side="right", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(buttons, text="📄 إنشاء وورد وبي دي إف", height=46, corner_radius=15, font=("Segoe UI", 15, "bold"), fg_color=GREEN, hover_color="#047857", command=create_document).pack(side="left", fill="x", expand=True, padx=(6, 0))

    def show_result_window(self, parent, output_path, pdf_path, pdf_error=""):
        result = self.make_modal("تم إنشاء الوثيقة", "680x400")
        box = ctk.CTkFrame(result, fg_color=BG)
        box.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(box, text="✅ تم إنشاء الوثيقة وحفظها في الأرشيف", font=("Segoe UI", 22, "bold"), text_color=TEXT).pack(pady=(8, 14))
        path_text = ctk.CTkTextbox(box, height=105, font=("Segoe UI", 13))
        path_text.pack(fill="x", pady=8)
        if pdf_path:
            path_text.insert("end", f"Word:\n{output_path}\n\nPDF:\n{pdf_path}")
        else:
            path_text.insert("end", f"Word:\n{output_path}\n\nPDF:\nلم يتم إنشاء PDF.\n\nالسبب:\n{pdf_error}")
        path_text.configure(state="disabled")
        buttons = ctk.CTkFrame(box, fg_color="transparent")
        buttons.pack(fill="x", pady=(18, 0))
        ctk.CTkButton(buttons, text="📄 فتح ملف وورد", height=40, command=lambda: open_file(output_path)).pack(side="right", fill="x", expand=True, padx=5)
        if pdf_path:
            ctk.CTkButton(buttons, text="📕 فتح PDF", height=40, command=lambda: open_file(pdf_path)).pack(side="right", fill="x", expand=True, padx=5)
            ctk.CTkButton(buttons, text="🖨️ طباعة PDF", height=40, fg_color=GREEN, hover_color="#047857", command=lambda: print_file(pdf_path)).pack(side="right", fill="x", expand=True, padx=5)
        else:
            ctk.CTkButton(buttons, text="📕 لم يتم إنشاء PDF", height=40, state="disabled").pack(side="right", fill="x", expand=True, padx=5)

    def confirm_delete_template(self, template_id):
        answer = messagebox.askyesno("تأكيد الحذف", "هل تريد حذف هذا النموذج؟\nسيتم حذف الاستمارة وربطها بالقالب، لكن الوثائق القديمة في الأرشيف لا تحذف.")
        if answer:
            try:
                delete_template(template_id)
                self.load_templates_cards()
            except Exception as e:
                messagebox.showerror("خطأ", f"تعذر حذف النموذج:\n{e}")
