import os
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox

from utils.paths import get_templates_dir
from database import (
    init_database,
    get_categories,
    get_templates_by_category,
    get_template_fields,
    add_template,
    get_template,
    delete_template,
    make_field_key,
    save_archive,
    save_customer,
    search_customers
)

from document_engine import (
    generate_word_document,
    generate_word_from_text_template,
    generate_simple_pdf,
    render_text_template
)

from print_manager import open_file, print_file


TEMPLATES_FOLDER = get_templates_dir()


def ensure_templates_folder():
    os.makedirs(TEMPLATES_FOLDER, exist_ok=True)


class DocumentsPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        try:
            init_database()
            ensure_templates_folder()
        except Exception as e:
            messagebox.showerror("خطأ", f"تعذر تهيئة قسم الوثائق:\n{e}")

        self.current_category_id = None
        self.current_category_name = None
        self.current_category_icon = None

        self.build_categories_ui()

    def clear_page(self):
        for widget in self.winfo_children():
            widget.destroy()

    def build_categories_ui(self):
        self.clear_page()

        title = ctk.CTkLabel(
            self,
            text="📄 قسم الوثائق",
            font=("Segoe UI", 30, "bold"),
            text_color="#111827"
        )
        title.pack(pady=(20, 10))

        subtitle = ctk.CTkLabel(
            self,
            text="اختر نوع الوثائق لإدارة النماذج والاستمارات",
            font=("Segoe UI", 15),
            text_color="#6B7280"
        )
        subtitle.pack(pady=(0, 30))

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(expand=True)

        try:
            categories = get_categories()
        except Exception as e:
            messagebox.showerror("خطأ", f"تعذر تحميل الأقسام:\n{e}")
            categories = []

        row = 0
        col = 0

        for category_id, name, icon in categories:
            card = ctk.CTkButton(
                grid,
                text=f"{icon}\n\n{name}",
                width=230,
                height=170,
                corner_radius=22,
                font=("Segoe UI", 20, "bold"),
                fg_color="#F3F4F6",
                hover_color="#E5E7EB",
                text_color="#111827",
                command=lambda cid=category_id, n=name, i=icon: self.open_category(cid, n, i)
            )
            card.grid(row=row, column=col, padx=18, pady=18)

            col += 1
            if col > 2:
                col = 0
                row += 1

    def open_category(self, category_id, category_name, category_icon):
        self.current_category_id = category_id
        self.current_category_name = category_name
        self.current_category_icon = category_icon

        self.clear_page()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 20))

        back_btn = ctk.CTkButton(
            header,
            text="↩ رجوع",
            width=100,
            height=36,
            command=self.build_categories_ui
        )
        back_btn.pack(side="left", padx=5)

        title = ctk.CTkLabel(
            header,
            text=f"{category_icon} {category_name}",
            font=("Segoe UI", 28, "bold"),
            text_color="#111827"
        )
        title.pack(side="right", padx=10)

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", pady=(0, 15))

        add_btn = ctk.CTkButton(
            actions,
            text="➕ إضافة نموذج جديد",
            height=42,
            width=190,
            font=("Segoe UI", 15, "bold"),
            command=self.open_add_template_window
        )
        add_btn.pack(side="right", padx=5)

        self.templates_area = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.templates_area.pack(fill="both", expand=True)

        self.load_templates_cards()

    def load_templates_cards(self):
        for widget in self.templates_area.winfo_children():
            widget.destroy()

        try:
            templates = get_templates_by_category(self.current_category_id)
        except Exception as e:
            messagebox.showerror("خطأ", f"تعذر تحميل النماذج:\n{e}")
            templates = []

        if not templates:
            empty = ctk.CTkLabel(
                self.templates_area,
                text="لا توجد نماذج بعد. اضغط على إضافة نموذج جديد.",
                font=("Segoe UI", 17),
                text_color="#6B7280"
            )
            empty.pack(pady=80)
            return

        grid = ctk.CTkFrame(self.templates_area, fg_color="transparent")
        grid.pack(pady=10)

        row = 0
        col = 0

        for item in templates:
            template_id = item[0]
            name = item[1]
            template_path = item[2]
            template_content = item[5] if len(item) > 5 else None

            card = ctk.CTkFrame(
                grid,
                width=260,
                height=195,
                corner_radius=20,
                fg_color="#F3F4F6"
            )
            card.grid(row=row, column=col, padx=16, pady=16)
            card.grid_propagate(False)

            title = ctk.CTkLabel(
                card,
                text=f"📄 {name}",
                font=("Segoe UI", 18, "bold"),
                text_color="#111827"
            )
            title.pack(pady=(18, 8))

            try:
                fields = get_template_fields(template_id)
            except Exception:
                fields = []

            info = ctk.CTkLabel(
                card,
                text=f"عدد الخانات: {len(fields)}",
                font=("Segoe UI", 13),
                text_color="#4B5563"
            )
            info.pack(pady=3)

            if template_path:
                status_text = "مرتبط بملف Word"
            elif template_content:
                status_text = "نموذج داخلي"
            else:
                status_text = "بدون قالب"

            status = ctk.CTkLabel(
                card,
                text=status_text,
                font=("Segoe UI", 12),
                text_color="#6B7280"
            )
            status.pack(pady=2)

            open_btn = ctk.CTkButton(
                card,
                text="فتح الاستمارة",
                width=170,
                height=34,
                command=lambda tid=template_id: self.open_fill_form_window(tid)
            )
            open_btn.pack(pady=(8, 6))

            delete_btn = ctk.CTkButton(
                card,
                text="حذف",
                width=170,
                height=30,
                fg_color="#DC2626",
                hover_color="#B91C1C",
                command=lambda tid=template_id: self.confirm_delete_template(tid)
            )
            delete_btn.pack()

            col += 1
            if col > 2:
                col = 0
                row += 1

    def open_add_template_window(self):
        try:
            self._open_add_template_window()
        except Exception as e:
            messagebox.showerror("خطأ في نافذة إضافة نموذج", str(e))

    def _open_add_template_window(self):
        window = ctk.CTkToplevel(self)
        window.title("إضافة نموذج جديد")
        window.geometry("840x780")
        window.focus()
        window.grab_set()

        selected_template_path = ctk.StringVar(value="")

        title = ctk.CTkLabel(
            window,
            text=f"إضافة نموذج داخل: {self.current_category_name}",
            font=("Segoe UI", 24, "bold")
        )
        title.pack(pady=(20, 10))

        container = ctk.CTkScrollableFrame(window)
        container.pack(fill="both", expand=True, padx=25, pady=20)

        name_label = ctk.CTkLabel(
            container,
            text="اسم النموذج",
            font=("Segoe UI", 15, "bold"),
            anchor="e"
        )
        name_label.pack(fill="x", pady=(15, 6))

        name_entry = ctk.CTkEntry(
            container,
            height=42,
            font=("Segoe UI", 15),
            placeholder_text="مثال: طلب وظيفة"
        )
        name_entry.pack(fill="x")

        fields_label = ctk.CTkLabel(
            container,
            text="خانات الاستمارة",
            font=("Segoe UI", 15, "bold"),
            anchor="e"
        )
        fields_label.pack(fill="x", pady=(18, 6))

        field_input_row = ctk.CTkFrame(container, fg_color="transparent")
        field_input_row.pack(fill="x")

        field_entry = ctk.CTkEntry(
            field_input_row,
            height=40,
            font=("Segoe UI", 14),
            placeholder_text="مثال: المستوى الدراسي"
        )
        field_entry.pack(side="right", fill="x", expand=True, padx=(0, 8))

        fields_list = []

        fields_box = ctk.CTkTextbox(
            container,
            height=150,
            font=("Segoe UI", 15)
        )
        fields_box.pack(fill="x", pady=12)

        def refresh_fields_box():
            fields_box.delete("1.0", "end")

            if not fields_list:
                fields_box.insert("end", "لم تضف أي خانة بعد.\n")
                return

            for index, field in enumerate(fields_list, start=1):
                key = make_field_key(field)
                fields_box.insert("end", f"{index}. {field}     ←     {{{{{key}}}}}\n")

        def add_field():
            value = field_entry.get().strip()

            if not value:
                return

            if value in fields_list:
                messagebox.showwarning("تنبيه", "هذه الخانة موجودة مسبقا")
                return

            fields_list.append(value)
            field_entry.delete(0, "end")
            refresh_fields_box()

        def remove_last_field():
            if fields_list:
                fields_list.pop()
                refresh_fields_box()

        add_field_btn = ctk.CTkButton(
            field_input_row,
            text="إضافة الخانة",
            width=130,
            height=40,
            command=add_field
        )
        add_field_btn.pack(side="left")

        remove_btn = ctk.CTkButton(
            container,
            text="حذف آخر خانة",
            width=140,
            height=34,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=remove_last_field
        )
        remove_btn.pack(anchor="e", pady=(0, 12))

        refresh_fields_box()

        template_label = ctk.CTkLabel(
            container,
            text="طريقة إنشاء القالب",
            font=("Segoe UI", 16, "bold"),
            anchor="e"
        )
        template_label.pack(fill="x", pady=(10, 6))

        path_label = ctk.CTkLabel(
            container,
            text="لم يتم اختيار ملف Word بعد",
            font=("Segoe UI", 13),
            text_color="#6B7280",
            anchor="e"
        )
        path_label.pack(fill="x", pady=(0, 8))

        def choose_word_template():
            file_path = filedialog.askopenfilename(
                title="اختر نموذج Word",
                filetypes=[
                    ("Word files", "*.docx"),
                    ("All files", "*.*")
                ]
            )

            if file_path:
                selected_template_path.set(file_path)
                path_label.configure(text=file_path)

        choose_btn = ctk.CTkButton(
            container,
            text="📎 رفع نموذج Word من الجهاز",
            height=40,
            command=choose_word_template
        )
        choose_btn.pack(fill="x", pady=(0, 12))

        internal_label = ctk.CTkLabel(
            container,
            text="أو اكتب النموذج داخل البرنامج",
            font=("Segoe UI", 15, "bold"),
            anchor="e"
        )
        internal_label.pack(fill="x", pady=(10, 6))

        editor = ctk.CTkTextbox(
            container,
            height=230,
            font=("Segoe UI", 15)
        )
        editor.pack(fill="x", pady=(0, 10))
        editor.insert(
            "end",
            "اكتب نص النموذج هنا...\n\nمثال:\nأنا الممضي أسفله {{الاسم}} {{اللقب}}\nالساكن بـ {{العنوان}}\nالهاتف: {{الهاتف}}\n"
        )

        note = ctk.CTkLabel(
            container,
            text="ملاحظة: إذا رفعت ملف Word سيستعمله البرنامج. إذا لم ترفع ملف Word سيستعمل النص المكتوب في المحرر الداخلي.",
            font=("Segoe UI", 13),
            text_color="#6B7280",
            wraplength=740,
            justify="right"
        )
        note.pack(fill="x", pady=(0, 15))

        def save_template_action():
            template_name = name_entry.get().strip()

            if not template_name:
                messagebox.showerror("خطأ", "اكتب اسم النموذج")
                return

            if not fields_list:
                messagebox.showerror("خطأ", "أضف خانات الاستمارة")
                return

            source_path = selected_template_path.get().strip()
            final_path = None
            template_content = editor.get("1.0", "end").strip()

            if source_path:
                safe_name = template_name.replace(" ", "_")
                final_path = os.path.join(TEMPLATES_FOLDER, f"{safe_name}.docx")

                try:
                    shutil.copy2(source_path, final_path)
                except Exception as e:
                    messagebox.showerror("خطأ", f"تعذر نسخ ملف Word:\n{e}")
                    return

            if not final_path and not template_content:
                messagebox.showerror("خطأ", "ارفع ملف Word أو اكتب النموذج داخل المحرر")
                return

            try:
                add_template(
                    category_id=self.current_category_id,
                    template_name=template_name,
                    fields=fields_list,
                    template_path=final_path,
                    template_content=template_content if not final_path else None
                )

                messagebox.showinfo("تم", "تم حفظ النموذج بنجاح")
                window.destroy()
                self.load_templates_cards()

            except Exception as e:
                messagebox.showerror("خطأ", f"تعذر حفظ النموذج:\n{e}")

        save_btn = ctk.CTkButton(
            container,
            text="💾 حفظ النموذج",
            height=46,
            font=("Segoe UI", 16, "bold"),
            command=save_template_action
        )
        save_btn.pack(fill="x", pady=10)

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

        window = ctk.CTkToplevel(self)
        window.title(template_name)
        window.geometry("760x760")
        window.focus()
        window.grab_set()

        title = ctk.CTkLabel(
            window,
            text=f"استمارة: {template_name}",
            font=("Segoe UI", 24, "bold")
        )
        title.pack(pady=(20, 10))

        form = ctk.CTkScrollableFrame(window)
        form.pack(fill="both", expand=True, padx=25, pady=20)

        entries = {}

        for field_id, field_label, field_key, field_order in fields:
            label = ctk.CTkLabel(
                form,
                text=field_label,
                font=("Segoe UI", 15, "bold"),
                anchor="e"
            )
            label.pack(fill="x", pady=(12, 5))

            entry = ctk.CTkEntry(
                form,
                height=40,
                font=("Segoe UI", 14),
                placeholder_text=field_label
            )
            entry.pack(fill="x")

            entries[field_key] = entry

        def collect_data():
            data = {}

            for field_id, field_label, field_key, field_order in fields:
                data[field_key] = entries[field_key].get().strip()

            return data

        def get_value(data, possible_labels):
            for label in possible_labels:
                key = make_field_key(label)
                if key in data and data[key]:
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

            preview = ctk.CTkToplevel(window)
            preview.title("معاينة")
            preview.geometry("720x640")
            preview.focus()
            preview.grab_set()

            preview_title = ctk.CTkLabel(
                preview,
                text="معاينة قبل إنشاء الوثيقة",
                font=("Segoe UI", 22, "bold")
            )
            preview_title.pack(pady=20)

            text = ctk.CTkTextbox(
                preview,
                font=("Segoe UI", 15)
            )
            text.pack(fill="both", expand=True, padx=20, pady=20)

            if template_content:
                text.insert("end", render_text_template(template_content, data))
            else:
                text.insert("end", f"النموذج: {template_name}\n")
                text.insert("end", f"القسم: {self.current_category_name}\n\n")

                for field_id, field_label, field_key, field_order in fields:
                    text.insert("end", f"{field_label}: {data.get(field_key, '')}\n")

            text.configure(state="disabled")

        def create_document():
            data = collect_data()

            if not template_path and not template_content:
                messagebox.showerror("خطأ", "هذا النموذج غير مرتبط بملف Word ولا يحتوي على نص داخلي.")
                return

            try:
                if template_path:
                    output_path = generate_word_document(
                        template_path=template_path,
                        data=data,
                        template_name=template_name
                    )
                else:
                    output_path = generate_word_from_text_template(
                        template_content=template_content,
                        data=data,
                        template_name=template_name
                    )

                pdf_path = generate_simple_pdf(
                    data=data,
                    template_name=template_name,
                    template_content=template_content
                )

                first_name, last_name, address, phone = save_customer_from_form(data)
                customer_name = f"{first_name} {last_name}".strip()

                save_archive(
                    customer_name=customer_name,
                    phone=phone,
                    document_type=self.current_category_name,
                    template_name=template_name,
                    word_path=output_path,
                    pdf_path=pdf_path
                )

                result_window = ctk.CTkToplevel(window)
                result_window.title("تم إنشاء الوثيقة")
                result_window.geometry("650x390")
                result_window.focus()
                result_window.grab_set()

                done_label = ctk.CTkLabel(
                    result_window,
                    text="✅ تم إنشاء الوثيقة وحفظها في الأرشيف",
                    font=("Segoe UI", 22, "bold")
                )
                done_label.pack(pady=(30, 15))

                path_text = ctk.CTkTextbox(
                    result_window,
                    height=100,
                    font=("Segoe UI", 13)
                )
                path_text.pack(fill="x", padx=25, pady=10)
                path_text.insert("end", f"Word:\n{output_path}\n\nPDF:\n{pdf_path}")
                path_text.configure(state="disabled")

                buttons = ctk.CTkFrame(result_window, fg_color="transparent")
                buttons.pack(fill="x", padx=25, pady=20)

                open_word_btn = ctk.CTkButton(
                    buttons,
                    text="📄 فتح Word",
                    height=40,
                    command=lambda: open_file(output_path)
                )
                open_word_btn.pack(side="right", fill="x", expand=True, padx=5)

                open_pdf_btn = ctk.CTkButton(
                    buttons,
                    text="📕 فتح PDF",
                    height=40,
                    command=lambda: open_file(pdf_path)
                )
                open_pdf_btn.pack(side="right", fill="x", expand=True, padx=5)

                print_btn = ctk.CTkButton(
                    buttons,
                    text="🖨️ طباعة PDF",
                    height=40,
                    fg_color="#059669",
                    hover_color="#047857",
                    command=lambda: print_file(pdf_path)
                )
                print_btn.pack(side="right", fill="x", expand=True, padx=5)

            except Exception as e:
                messagebox.showerror("خطأ", f"تعذر إنشاء الوثيقة:\n{e}")

        preview_btn = ctk.CTkButton(
            form,
            text="👁 معاينة",
            height=45,
            font=("Segoe UI", 16, "bold"),
            command=preview_data
        )
        preview_btn.pack(fill="x", pady=(25, 10))

        create_btn = ctk.CTkButton(
            form,
            text="📄 إنشاء Word + PDF",
            height=45,
            font=("Segoe UI", 16, "bold"),
            command=create_document
        )
        create_btn.pack(fill="x", pady=(0, 20))

    def confirm_delete_template(self, template_id):
        answer = messagebox.askyesno(
            "تأكيد الحذف",
            "هل تريد حذف هذا النموذج؟"
        )

        if answer:
            try:
                delete_template(template_id)
                self.load_templates_cards()
            except Exception as e:
                messagebox.showerror("خطأ", f"تعذر حذف النموذج:\n{e}")
