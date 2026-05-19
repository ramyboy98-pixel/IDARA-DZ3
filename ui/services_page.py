# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import customtkinter as ctk
from tkinter import Menu, messagebox
from PIL import Image

from database import (
    count_services_today,
    log_service_operation,
    get_service_links,
    add_service_link,
    update_service_link,
    delete_service_link,
    search_service_operations,
)


BG = "#F5F7FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"
BLUE = "#2563EB"
HOVER = "#EFF6FF"
GREEN = "#059669"
RED = "#DC2626"

SERVICES = [
    {"key": "defense", "name": "وزارة الدفاع الوطني", "logo": "assets/services/defense.png"},
    {"key": "foreign_affairs", "name": "وزارة الخارجية", "logo": "assets/services/foreign_affairs.png"},
    {"key": "interior", "name": "وزارة الداخلية", "logo": "assets/services/interior.png"},
    {"key": "justice", "name": "وزارة العدل", "logo": "assets/services/justice.png"},
    {"key": "finance", "name": "وزارة المالية", "logo": "assets/services/finance.png"},
    {"key": "energy_mines", "name": "وزارة الطاقة و المناجم", "logo": "assets/services/energy_mines.png"},
    {"key": "moudjahidine", "name": "وزارة المجاهدين", "logo": "assets/services/moudjahidine.png"},
    {"key": "religious_affairs", "name": "وزارة الشؤون الدينية و الأوقاف", "logo": "assets/services/religious_affairs.png"},
    {"key": "education", "name": "وزارة التربية", "logo": "assets/services/education.png"},
    {"key": "higher_education", "name": "وزارة التعليم العالي", "logo": "assets/services/higher_education.png"},
    {"key": "vocational_training", "name": "وزارة التكوين و التعليم المهنيين", "logo": "assets/services/vocational_training.png"},
    {"key": "culture", "name": "وزارة الثقافة", "logo": "assets/services/culture.png"},
    {"key": "youth_sports", "name": "وزارة الشباب و الرياضة", "logo": "assets/services/youth_sports.png"},
    {"key": "post_telecom", "name": "وزارة البريد و المواصلات", "logo": "assets/services/post_telecom.png"},
    {"key": "solidarity", "name": "وزارة التضامن", "logo": "assets/services/solidarity.png"},
    {"key": "industry", "name": "وزارة الصناعة", "logo": "assets/services/industry.png"},
    {"key": "agriculture", "name": "وزارة الفلاحة", "logo": "assets/services/agriculture.png"},
    {"key": "housing", "name": "وزارة السكن", "logo": "assets/services/housing.png"},
    {"key": "commerce", "name": "وزارة التجارة", "logo": "assets/services/commerce.png"},
    {"key": "communication", "name": "وزارة الاتصال", "logo": "assets/services/communication.png"},
    {"key": "public_works", "name": "وزارة الاشغال العمومية", "logo": "assets/services/public_works.png"},
    {"key": "water_resources", "name": "وزارة الري", "logo": "assets/services/water_resources.png"},
    {"key": "transport", "name": "وزارة النقل", "logo": "assets/services/transport.png"},
    {"key": "tourism", "name": "وزارة السياحة", "logo": "assets/services/tourism.png"},
    {"key": "health", "name": "وزارة الصحة", "logo": "assets/services/health.png"},
    {"key": "labor", "name": "وزارة العمل", "logo": "assets/services/labor.png"},
    {"key": "environment", "name": "وزارة البيئة", "logo": "assets/services/environment.png"},
    {"key": "fishing", "name": "وزارة الصيد البحري", "logo": "assets/services/fishing.png"},
    {"key": "knowledge_economy", "name": "وزارة اقتصاد المعرفة", "logo": "assets/services/knowledge_economy.png"},
    {"key": "algerie_telecom", "name": "اتصالات الجزائر", "logo": "assets/services/algerie_telecom.png"},
    {"key": "algerie_poste", "name": "بريد الجزائر", "logo": "assets/services/algerie_poste.png"},
    {"key": "e_payment", "name": "الدفع الالكتروني", "logo": "assets/services/e_payment.png"},
    {"key": "red_crescent", "name": "الهلال الاحمر الجزائري", "logo": "assets/services/red_crescent.png"},
    {"key": "tramway", "name": "تسيير خطوط الترامواي", "logo": "assets/services/tramway.png"},
    {"key": "elections", "name": "السلطة المستقلة للانتخابات", "logo": "assets/services/elections.png"},
    {"key": "retirement_fund", "name": "الصندوق الوطني للمتقاعدين", "logo": "assets/services/retirement_fund.png"},
    {"key": "cnas", "name": "الضمان الاجتماعي للاجراء", "logo": "assets/services/cnas.png"},
    {"key": "casnos", "name": "الضمان الاجتماعي لغير الاجراء", "logo": "assets/services/casnos.png"},
    {"key": "onefd", "name": "المراسلة ONEFD", "logo": "assets/services/onefd.png"},
    {"key": "anem", "name": "وكالة التشغيل ANEM", "logo": "assets/services/anem.png"},
    {"key": "public_service", "name": "الوظيف العمومي", "logo": "assets/services/public_service.png"},
    {"key": "taxes", "name": "المديرية العامة للضرائب", "logo": "assets/services/taxes.png"},
    {"key": "public_procurement", "name": "الصفقات العمومية", "logo": "assets/services/public_procurement.png"},
]


class ServicesPage(ctk.CTkFrame):
    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.today_label = None
        self.search_entry = None
        self.cards_grid = None
        self.links_box = None
        self.current_service = None
        self.logo_cache = {}
        self.build_ui()

    def resource_path(self, relative_path):
        base_path = getattr(sys, "_MEIPASS", os.path.abspath(os.getcwd()))
        return os.path.join(base_path, relative_path)

    def get_logo_image(self, relative_path):
        if relative_path in self.logo_cache:
            return self.logo_cache[relative_path]

        path = self.resource_path(relative_path)
        if not os.path.exists(path):
            return None

        try:
            image = Image.open(path)
            image.thumbnail((112, 112), Image.LANCZOS)
            logo = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
            self.logo_cache[relative_path] = logo
            return logo
        except Exception:
            return None

    def build_ui(self):
        self.render_services_home()

    def clear_page(self):
        for widget in self.winfo_children():
            widget.destroy()

    def render_services_home(self):
        self.current_service = None
        self.clear_page()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 14))

        ctk.CTkLabel(
            header,
            text="خدمات إلكترونية",
            font=("Segoe UI", 30, "bold"),
            text_color=TEXT,
        ).pack(anchor="e")

        ctk.CTkLabel(
            header,
            text="اختر الوزارة أو المصلحة للدخول إلى قائمة الروابط الخاصة بها.",
            font=("Segoe UI", 14),
            text_color=MUTED,
        ).pack(anchor="e", pady=(4, 0))

        top_bar = ctk.CTkFrame(self, fg_color=CARD, corner_radius=20, border_width=1, border_color=BORDER)
        top_bar.pack(fill="x", pady=(0, 12), anchor="n")

        self.today_label = ctk.CTkLabel(
            top_bar,
            text=f"خدمات اليوم: {count_services_today()}",
            font=("Segoe UI", 17, "bold"),
            text_color=TEXT,
        )
        self.today_label.pack(side="right", padx=16, pady=14)

        self.search_entry = ctk.CTkEntry(
            top_bar,
            placeholder_text="بحث في الوزارات والمصالح...",
            width=360,
            height=40,
            corner_radius=14,
            font=("Segoe UI", 14),
            justify="right",
        )
        self.search_entry.pack(side="right", padx=10, pady=14)
        self.search_entry.bind("<KeyRelease>", lambda _event=None: self.render_service_cards())

        clear_btn = ctk.CTkButton(
            top_bar,
            text="مسح",
            width=75,
            height=38,
            corner_radius=13,
            fg_color="#F3F4F6",
            hover_color="#E5E7EB",
            text_color=TEXT,
            command=self.clear_search,
        )
        clear_btn.pack(side="left", padx=16, pady=14)

        self.cards_grid = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.cards_grid.pack(fill="both", expand=True, anchor="n", pady=(0, 8))
        self.render_service_cards()

    def clear_search(self):
        if self.search_entry:
            self.search_entry.delete(0, "end")
        self.render_service_cards()

    def render_service_cards(self):
        if not self.cards_grid:
            return

        for widget in self.cards_grid.winfo_children():
            widget.destroy()

        keyword = self.search_entry.get().strip() if self.search_entry else ""
        services = [s for s in SERVICES if not keyword or keyword in s["name"]]

        if not services:
            ctk.CTkLabel(
                self.cards_grid,
                text="لا توجد مصلحة مطابقة للبحث.",
                font=("Segoe UI", 15),
                text_color=MUTED,
            ).grid(row=0, column=0, sticky="e", padx=10, pady=18)
            return

        for col in range(4):
            self.cards_grid.grid_columnconfigure(col, weight=1, uniform="service_cards")

        for index, service in enumerate(services):
            row, col = divmod(index, 4)
            self.service_card(self.cards_grid, service, row, col)

    def service_card(self, parent, service, row, col):
        card = ctk.CTkFrame(
            parent,
            width=210,
            height=210,
            corner_radius=24,
            fg_color=CARD,
            border_width=1,
            border_color=BORDER,
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="n")
        card.grid_propagate(False)

        logo = self.get_logo_image(service["logo"])
        if logo:
            logo_label = ctk.CTkLabel(card, text="", image=logo)
        else:
            logo_label = ctk.CTkLabel(card, text="🌐", font=("Segoe UI Emoji", 54), text_color=TEXT)
        logo_label.pack(pady=(30, 14))

        name_label = ctk.CTkLabel(
            card,
            text=service["name"],
            font=("Segoe UI", 17, "bold"),
            text_color=TEXT,
            wraplength=180,
            justify="center",
        )
        name_label.pack(pady=(0, 8))

        def open_card(_event=None):
            self.open_service_links(service)

        def make_clickable(widget):
            try:
                widget.configure(cursor="hand2")
            except Exception:
                pass
            widget.bind("<Button-1>", open_card)

        for widget in (card, logo_label, name_label):
            make_clickable(widget)

        def enter(_event=None):
            card.configure(fg_color=HOVER, border_color=BLUE)
            name_label.configure(text_color=BLUE)

        def leave(_event=None):
            card.configure(fg_color=CARD, border_color=BORDER)
            name_label.configure(text_color=TEXT)

        for widget in (card, logo_label, name_label):
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)

    def open_service_links(self, service):
        self.current_service = service
        self.clear_page()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 12))

        back_btn = ctk.CTkButton(
            header,
            text="رجوع ←",
            width=110,
            height=38,
            corner_radius=12,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.render_services_home,
        )
        back_btn.pack(side="left")

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="right", fill="x", expand=True)

        ctk.CTkLabel(
            title_frame,
            text=service["name"],
            font=("Segoe UI", 30, "bold"),
            text_color=TEXT,
        ).pack(anchor="e")

        ctk.CTkLabel(
            title_frame,
            text="قائمة الروابط الخاصة بهذه المصلحة. اضغط على الرابط لفتحه، واضغط بزر الفأرة الأيمن للتعديل أو الحذف.",
            font=("Segoe UI", 14),
            text_color=MUTED,
        ).pack(anchor="e", pady=(4, 0))

        toolbar = ctk.CTkFrame(self, fg_color=CARD, corner_radius=20, border_width=1, border_color=BORDER)
        toolbar.pack(fill="x", pady=(0, 14))

        add_btn = ctk.CTkButton(
            toolbar,
            text="+ إضافة رابط",
            height=42,
            width=160,
            corner_radius=14,
            fg_color=BLUE,
            hover_color="#1D4ED8",
            font=("Segoe UI", 14, "bold"),
            command=lambda: self.open_link_dialog(service["key"]),
        )
        add_btn.pack(side="right", padx=16, pady=14)

        self.links_box = ctk.CTkScrollableFrame(self, fg_color=CARD, corner_radius=20, border_width=1, border_color=BORDER)
        self.links_box.pack(fill="both", expand=True)
        self.render_links()

    def render_links(self):
        if not self.links_box or not self.current_service:
            return

        for widget in self.links_box.winfo_children():
            widget.destroy()

        rows = get_service_links(self.current_service["key"])

        if not rows:
            ctk.CTkLabel(
                self.links_box,
                text="لا توجد روابط بعد. اضغط على زر إضافة رابط.",
                font=("Segoe UI", 16),
                text_color=MUTED,
            ).pack(anchor="center", pady=30)
            return

        for row in rows:
            link_id, service_key, title, url, created_at, updated_at = row
            self.link_row(link_id, title, url)

    def link_row(self, link_id, title, url):
        row = ctk.CTkFrame(self.links_box, fg_color="#FFFFFF", corner_radius=0, height=82)
        row.pack(fill="x", padx=8, pady=0)
        row.pack_propagate(False)

        icon_label = ctk.CTkLabel(row, text="🌐", font=("Segoe UI Emoji", 30), text_color=TEXT)
        icon_label.pack(side="right", padx=(12, 16))

        text_box = ctk.CTkFrame(row, fg_color="transparent")
        text_box.pack(side="right", fill="both", expand=True, padx=6)

        title_label = ctk.CTkLabel(
            text_box,
            text=title,
            font=("Segoe UI", 20, "bold"),
            text_color=TEXT,
            anchor="e",
        )
        title_label.pack(anchor="e", pady=(12, 0))

        url_label = ctk.CTkLabel(
            text_box,
            text=url,
            font=("Segoe UI", 12),
            text_color=MUTED,
            anchor="e",
        )
        url_label.pack(anchor="e")

        separator = ctk.CTkFrame(self.links_box, fg_color=BORDER, height=1)
        separator.pack(fill="x", padx=10)

        def open_link(_event=None):
            self.open_link(title, url)

        def show_menu(event):
            self.show_link_context_menu(event, link_id, title, url)

        for widget in (row, icon_label, text_box, title_label, url_label):
            try:
                widget.configure(cursor="hand2")
            except Exception:
                pass
            widget.bind("<Button-1>", open_link)
            widget.bind("<Button-3>", show_menu)

    def show_link_context_menu(self, event, link_id, title, url):
        menu = Menu(self, tearoff=0)
        menu.add_command(label="تعديل", command=lambda: self.open_link_dialog(self.current_service["key"], link_id, title, url))
        menu.add_command(label="حذف", command=lambda: self.confirm_delete_link(link_id))
        menu.tk_popup(event.x_root, event.y_root)

    def open_link_dialog(self, service_key, link_id=None, title="", url=""):
        dialog = ctk.CTkToplevel(self)
        dialog.title("تعديل رابط" if link_id else "إضافة رابط")
        dialog.geometry("520x300")
        dialog.resizable(False, False)
        dialog.grab_set()

        box = ctk.CTkFrame(dialog, fg_color=BG)
        box.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(
            box,
            text="اسم الرابط",
            font=("Segoe UI", 15, "bold"),
            text_color=TEXT,
        ).pack(anchor="e", pady=(4, 5))

        title_entry = ctk.CTkEntry(box, height=42, justify="right", font=("Segoe UI", 14))
        title_entry.pack(fill="x")
        title_entry.insert(0, title or "")

        ctk.CTkLabel(
            box,
            text="الرابط",
            font=("Segoe UI", 15, "bold"),
            text_color=TEXT,
        ).pack(anchor="e", pady=(14, 5))

        url_entry = ctk.CTkEntry(box, height=42, justify="left", font=("Segoe UI", 14))
        url_entry.pack(fill="x")
        url_entry.insert(0, url or "")

        def save():
            new_title = title_entry.get().strip()
            new_url = url_entry.get().strip()

            if not new_title or not new_url:
                messagebox.showwarning("تنبيه", "أدخل اسم الرابط والرابط.")
                return

            if link_id:
                update_service_link(link_id, new_title, new_url)
            else:
                add_service_link(service_key, new_title, new_url)

            dialog.destroy()
            self.render_links()

        save_btn = ctk.CTkButton(
            box,
            text="حفظ",
            height=42,
            corner_radius=14,
            fg_color=GREEN,
            hover_color="#047857",
            font=("Segoe UI", 14, "bold"),
            command=save,
        )
        save_btn.pack(side="right", padx=(0, 8), pady=20)

        cancel_btn = ctk.CTkButton(
            box,
            text="إلغاء",
            height=42,
            corner_radius=14,
            fg_color="#6B7280",
            hover_color="#4B5563",
            font=("Segoe UI", 14, "bold"),
            command=dialog.destroy,
        )
        cancel_btn.pack(side="right", pady=20)

    def confirm_delete_link(self, link_id):
        if messagebox.askyesno("تأكيد الحذف", "هل تريد حذف هذا الرابط؟"):
            delete_service_link(link_id)
            self.render_links()

    def open_link(self, title, url):
        try:
            service_name = self.current_service["name"] if self.current_service else "خدمة إلكترونية"
            log_service_operation(f"{service_name} - {title}", url)
            self.refresh_counter()
            if self.app:
                self.app.toast(f"تم فتح: {title}", "success")
            webbrowser.open(url)
        except Exception as exc:
            messagebox.showerror("خطأ", f"تعذر فتح الرابط:\n{exc}")

    def refresh_counter(self):
        if self.today_label:
            self.today_label.configure(text=f"خدمات اليوم: {count_services_today()}")
