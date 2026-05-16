import os
import customtkinter as ctk
from tkinter import messagebox

from database import search_archive, search_customers, search_templates_all, search_service_operations
from print_manager import open_file

BG = "#F5F7FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"
BLUE = "#2563EB"
GREEN = "#059669"
GRAY = "#6B7280"


class SearchPage(ctk.CTkFrame):

    def __init__(self, parent, query="", app=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.query = (query or "").strip()
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(6, 16))

        title_text = "نتائج البحث"
        if self.query:
            title_text = f"نتائج البحث عن: {self.query}"

        ctk.CTkLabel(
            header,
            text=title_text,
            font=("Segoe UI", 28, "bold"),
            text_color=TEXT,
        ).pack(anchor="e")

        ctk.CTkLabel(
            header,
            text="البحث يشمل النماذج، الأرشيف، الخدمات الإلكترونية، والزبائن المحفوظين.",
            font=("Segoe UI", 14),
            text_color=MUTED,
        ).pack(anchor="e", pady=(6, 0))

        if not self.query:
            self.empty_state("اكتب كلمة في خانة البحث ثم اضغط Enter أو زر بحث.")
            return

        results_box = ctk.CTkScrollableFrame(self, fg_color="transparent")
        results_box.pack(fill="both", expand=True)

        templates = search_templates_all(self.query)
        archive = search_archive(self.query)
        customers = search_customers(self.query)
        services = search_service_operations(self.query)

        total = len(templates) + len(archive) + len(customers) + len(services)
        if total == 0:
            self.empty_state("لا توجد نتائج مطابقة.")
            return

        self.section_title(results_box, f"النماذج والوثائق ({len(templates)})")
        if templates:
            for row in templates[:20]:
                self.template_result(results_box, row)
        else:
            self.small_note(results_box, "لا توجد نماذج مطابقة.")

        self.section_title(results_box, f"الأرشيف ({len(archive)})")
        if archive:
            for row in archive[:20]:
                self.archive_result(results_box, row)
        else:
            self.small_note(results_box, "لا توجد وثائق محفوظة مطابقة.")

        self.section_title(results_box, f"الخدمات الإلكترونية ({len(services)})")
        if services:
            for row in services[:20]:
                self.service_result(results_box, row)
        else:
            self.small_note(results_box, "لا توجد خدمات إلكترونية مطابقة.")

        self.section_title(results_box, f"الزبائن ({len(customers)})")
        if customers:
            for row in customers[:20]:
                self.customer_result(results_box, row)
        else:
            self.small_note(results_box, "لا يوجد زبائن مطابقون.")

    def empty_state(self, text):
        box = ctk.CTkFrame(self, fg_color=CARD, corner_radius=22, border_width=1, border_color=BORDER)
        box.pack(fill="both", expand=True, pady=(20, 0))
        ctk.CTkLabel(box, text="🔎", font=("Segoe UI Emoji", 44)).pack(pady=(70, 8))
        ctk.CTkLabel(box, text=text, font=("Segoe UI", 18, "bold"), text_color=TEXT).pack()

    def section_title(self, parent, text):
        ctk.CTkLabel(
            parent,
            text=text,
            font=("Segoe UI", 20, "bold"),
            text_color=TEXT,
        ).pack(anchor="e", pady=(18, 8), padx=4)

    def small_note(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Segoe UI", 13), text_color=MUTED).pack(anchor="e", padx=12, pady=(0, 8))

    def result_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
        card.pack(fill="x", pady=6)
        return card

    def template_result(self, parent, row):
        template_id, template_name, category_name, updated_at, has_word, has_text = row
        card = self.result_card(parent)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(side="right", fill="both", expand=True, padx=16, pady=12)
        ctk.CTkLabel(body, text=f"📄 {template_name}", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(anchor="e")
        source = "قالب وورد" if has_word else "محرر داخلي" if has_text else "بدون قالب"
        ctk.CTkLabel(body, text=f"القسم: {category_name}  |  النوع: {source}  |  آخر تعديل: {updated_at}", font=("Segoe UI", 13), text_color=MUTED).pack(anchor="e", pady=(4, 0))
        if self.app:
            ctk.CTkButton(card, text="فتح الوثائق", width=120, height=34, fg_color=BLUE, command=self.app.show_documents).pack(side="left", padx=14, pady=12)

    def archive_result(self, parent, row):
        archive_id, customer_name, phone, document_type, template_name, word_path, pdf_path, created_at = row
        card = self.result_card(parent)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(side="right", fill="both", expand=True, padx=16, pady=12)
        title = template_name or document_type or "وثيقة محفوظة"
        ctk.CTkLabel(body, text=f"🗂️ {title}", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(anchor="e")
        ctk.CTkLabel(body, text=f"الزبون: {customer_name or '-'}  |  الهاتف: {phone or '-'}  |  التاريخ: {created_at}", font=("Segoe UI", 13), text_color=MUTED).pack(anchor="e", pady=(4, 0))

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(side="left", padx=12, pady=10)
        if word_path:
            ctk.CTkButton(buttons, text="وورد", width=72, height=32, fg_color=BLUE, command=lambda p=word_path: self.safe_open(p)).pack(side="right", padx=3)
        if pdf_path:
            ctk.CTkButton(buttons, text="PDF", width=72, height=32, fg_color=GREEN, command=lambda p=pdf_path: self.safe_open(p)).pack(side="right", padx=3)

    def service_result(self, parent, row):
        operation_id, service_name, service_url, customer_name, phone, notes, created_at = row
        card = self.result_card(parent)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(side="right", fill="both", expand=True, padx=16, pady=12)
        ctk.CTkLabel(body, text=f"🌐 {service_name}", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(anchor="e")
        ctk.CTkLabel(body, text=f"التاريخ: {created_at}  |  الرابط: {service_url or '-'}", font=("Segoe UI", 13), text_color=MUTED).pack(anchor="e", pady=(4, 0))
        if service_url:
            ctk.CTkButton(card, text="فتح", width=90, height=34, fg_color=BLUE, command=lambda p=service_url: self.safe_open_url(p)).pack(side="left", padx=14, pady=12)

    def customer_result(self, parent, row):
        customer_id, first_name, last_name, address, phone = row
        card = self.result_card(parent)
        name = f"{first_name or ''} {last_name or ''}".strip() or "زبون بدون اسم"
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(body, text=f"👥 {name}", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(anchor="e")
        ctk.CTkLabel(body, text=f"الهاتف: {phone or '-'}  |  العنوان: {address or '-'}", font=("Segoe UI", 13), text_color=MUTED).pack(anchor="e", pady=(4, 0))

    def safe_open_url(self, url):
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as exc:
            messagebox.showerror("خطأ", f"تعذر فتح الرابط:\n{exc}")

    def safe_open(self, path):
        try:
            if not path or not os.path.exists(path):
                messagebox.showwarning("تنبيه", "الملف غير موجود في هذا المسار.")
                return
            open_file(path)
        except Exception as exc:
            messagebox.showerror("خطأ", f"تعذر فتح الملف:\n{exc}")
