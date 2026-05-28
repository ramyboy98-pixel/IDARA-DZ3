# -*- coding: utf-8 -*-
import customtkinter as ctk
import webbrowser

from database import (
    count_documents_today,
    count_services_today,
    search_archive,
    search_service_operations,
    get_favorites,
)


BG = "#F5F7FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"
BLUE = "#2563EB"
GRAY_BTN = "#F3F4F6"


class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.build_ui()

    def build_ui(self):
        self.hero()
        self.stats()
        self.quick_actions()
        self.recent_and_favorites()

    def hero(self):
        box = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=22,
            border_width=1,
            border_color=BORDER,
        )
        box.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            box,
            text="IDARA DZ",
            font=("Segoe UI", 30, "bold"),
            text_color=TEXT,
        ).pack(anchor="e", padx=24, pady=(22, 4))

        ctk.CTkLabel(
            box,
            text="برنامج مكتبي لإدارة الوثائق، النماذج، الأرشيف والخدمات الإلكترونية.",
            font=("Segoe UI", 15),
            text_color=MUTED,
        ).pack(anchor="e", padx=24, pady=(0, 22))

    def stats(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=(0, 20))

        stats = [
            ("📄", "وثائق اليوم", str(self.safe_count(count_documents_today))),
            ("🌐", "خدمات اليوم", str(self.safe_count(count_services_today))),
        ]

        for icon, label, value in stats:
            card = ctk.CTkFrame(row, fg_color=CARD, corner_radius=20, border_width=1, border_color=BORDER)
            card.pack(side="right", fill="x", expand=True, padx=8)

            ctk.CTkLabel(card, text=icon, font=("Segoe UI Emoji", 30), text_color=TEXT).pack(anchor="e", padx=18, pady=(16, 2))
            ctk.CTkLabel(card, text=value, font=("Segoe UI", 25, "bold"), text_color=TEXT).pack(anchor="e", padx=18)
            ctk.CTkLabel(card, text=label, font=("Segoe UI", 14), text_color=MUTED).pack(anchor="e", padx=18, pady=(0, 16))

    def quick_actions(self):
        box = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=22,
            border_width=1,
            border_color=BORDER,
        )
        box.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            box,
            text="اختصارات سريعة",
            font=("Segoe UI", 24, "bold"),
            text_color=TEXT,
        ).pack(anchor="e", padx=24, pady=(20, 14))

        buttons = ctk.CTkFrame(box, fg_color="transparent")
        buttons.pack(fill="x", padx=24, pady=(0, 24))

        self.action_button(buttons, "📄 وثيقة جديدة", self.goto_documents).pack(side="right", fill="x", expand=True, padx=7)
        self.action_button(buttons, "📁 فتح الأرشيف", self.goto_archive).pack(side="right", fill="x", expand=True, padx=7)
        self.action_button(buttons, "🌐 الخدمات الإلكترونية", self.goto_services).pack(side="right", fill="x", expand=True, padx=7)

    def action_button(self, parent, text, command):
        return ctk.CTkButton(
            parent,
            text=text,
            height=46,
            corner_radius=15,
            font=("Segoe UI", 15, "bold"),
            fg_color=GRAY_BTN,
            hover_color="#E5E7EB",
            text_color=TEXT,
            command=command,
        )

    def recent_and_favorites(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="both", expand=True)

        recent_card = ctk.CTkFrame(row, fg_color=CARD, corner_radius=22, border_width=1, border_color=BORDER)
        recent_card.pack(side="right", fill="both", expand=True, padx=(8, 0))

        fav_card = ctk.CTkFrame(row, fg_color=CARD, corner_radius=22, border_width=1, border_color=BORDER)
        fav_card.pack(side="right", fill="both", expand=True, padx=(0, 8))

        self.fill_recent(recent_card)
        self.fill_favorites(fav_card)

    def fill_recent(self, parent):
        ctk.CTkLabel(
            parent,
            text="آخر العمليات",
            font=("Segoe UI", 22, "bold"),
            text_color=TEXT,
        ).pack(anchor="e", padx=20, pady=(18, 10))

        items = []

        # آخر الوثائق
        try:
            archive_rows = search_archive("", "", "")[:4]
        except Exception:
            archive_rows = []

        for row in archive_rows:
            _id, customer, phone, doc_type, template_name, word_path, pdf_path, created_at = row
            title = template_name or doc_type or "وثيقة"
            subtitle = f"{customer or ''}  •  {phone or ''}  •  {created_at or ''}".strip(" •")
            items.append({
                "icon": "📄",
                "title": title,
                "subtitle": subtitle,
                "command": self.goto_archive,
            })

        # آخر الخدمات المفتوحة
        try:
            service_rows = search_service_operations("", "", "")[:4]
        except Exception:
            service_rows = []

        for row in service_rows:
            service_id, service_name, service_url, customer_name, phone, notes, created_at = row
            title = service_name or "خدمة إلكترونية"
            subtitle = f"{created_at or ''}  •  {service_url or ''}".strip(" •")

            if service_url:
                command = lambda url=service_url: self.open_url(url)
            else:
                command = self.goto_services

            items.append({
                "icon": "🌐",
                "title": title,
                "subtitle": subtitle,
                "command": command,
            })

        if not items:
            self.empty_label(parent, "لا توجد عمليات حديثة.")
            return

        for item in items[:8]:
            self.info_row(
                parent,
                item["icon"],
                item["title"],
                item["subtitle"],
                command=item["command"],
            )

    def fill_favorites(self, parent):
        ctk.CTkLabel(
            parent,
            text="المفضلة ⭐",
            font=("Segoe UI", 22, "bold"),
            text_color=TEXT,
        ).pack(anchor="e", padx=20, pady=(18, 10))

        try:
            favorites = get_favorites(limit=8)
        except Exception:
            favorites = []

        if not favorites:
            self.empty_label(parent, "لا توجد مفضلة بعد. أضف نجمة من الوثائق أو الخدمات.")
            return

        for fav in favorites:
            # يدعم أكثر من شكل راجع من قاعدة البيانات
            favorite_id = fav[0] if len(fav) > 0 else None
            item_type = fav[1] if len(fav) > 1 else ""
            item_key = fav[2] if len(fav) > 2 else ""
            title = fav[3] if len(fav) > 3 else ""
            subtitle = fav[4] if len(fav) > 4 else ""

            icon = self.favorite_icon(item_type)
            command = lambda t=item_type, k=item_key, title=title: self.open_favorite(t, k, title)
            self.info_row(parent, icon, title or item_key, subtitle or item_type, command=command)

    def info_row(self, parent, icon, title, subtitle="", command=None):
        row = ctk.CTkFrame(parent, fg_color="#F9FAFB", corner_radius=14)
        row.pack(fill="x", padx=16, pady=5)

        ctk.CTkLabel(row, text=icon, font=("Segoe UI Emoji", 19), text_color=TEXT).pack(side="right", padx=(12, 6), pady=10)

        text_box = ctk.CTkFrame(row, fg_color="transparent")
        text_box.pack(side="right", fill="x", expand=True, padx=(4, 8), pady=8)

        title_label = ctk.CTkLabel(
            text_box,
            text=title,
            font=("Segoe UI", 14, "bold"),
            text_color=TEXT,
            anchor="e",
        )
        title_label.pack(fill="x")

        if subtitle:
            ctk.CTkLabel(
                text_box,
                text=subtitle,
                font=("Segoe UI", 11),
                text_color=MUTED,
                anchor="e",
            ).pack(fill="x", pady=(2, 0))

        if command:
            for widget in (row, text_box, title_label):
                try:
                    widget.configure(cursor="hand2")
                except Exception:
                    pass
                widget.bind("<Button-1>", lambda _e=None, cmd=command: cmd())

            def enter(_e=None):
                row.configure(fg_color="#EFF6FF")

            def leave(_e=None):
                row.configure(fg_color="#F9FAFB")

            for widget in (row, text_box, title_label):
                widget.bind("<Enter>", enter)
                widget.bind("<Leave>", leave)

    def empty_label(self, parent, text):
        ctk.CTkLabel(
            parent,
            text=text,
            font=("Segoe UI", 14),
            text_color=MUTED,
            wraplength=360,
            justify="center",
        ).pack(anchor="center", padx=20, pady=26)

    def favorite_icon(self, item_type):
        item_type = str(item_type or "").lower()
        if "service_link" in item_type or "رابط" in item_type:
            return "🔗"
        if "service" in item_type or "خدمة" in item_type:
            return "🌐"
        if "template" in item_type or "document" in item_type or "نموذج" in item_type:
            return "📄"
        return "⭐"

    def open_url(self, url):
        url = str(url or "").strip()
        if not url:
            self.goto_services()
            return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)

    def open_favorite(self, item_type, item_key, title=""):
        item_type = str(item_type or "").lower()
        item_key = str(item_key or "").strip()

        # رابط خدمة: افتح الرابط مباشرة إذا كان item_key رابطًا
        if "service_link" in item_type or item_key.startswith(("http://", "https://")):
            if item_key.startswith(("http://", "https://")):
                webbrowser.open(item_key)
            else:
                self.goto_services()
            return

        # خدمة/وزارة: افتح صفحة الخدمات
        if "service" in item_type:
            self.goto_services()
            try:
                # بعد تحميل صفحة الخدمات، افتح الخدمة المحددة إذا كان المفتاح هو service_key
                if self.app and hasattr(self.app, "content"):
                    self.after(120, lambda: self.try_open_service_key(item_key))
            except Exception:
                pass
            return

        # نموذج/وثيقة: افتح قسم الوثائق
        if "template" in item_type or "document" in item_type:
            self.goto_documents()
            return

        self.goto_services()

    def try_open_service_key(self, service_key):
        try:
            for widget in self.app.content.winfo_children():
                if hasattr(widget, "open_service_by_key"):
                    widget.open_service_by_key(service_key)
                    return
        except Exception:
            pass

    def goto_documents(self):
        if self.app and hasattr(self.app, "show_documents"):
            self.app.show_documents()

    def goto_services(self):
        if self.app and hasattr(self.app, "show_services"):
            self.app.show_services()

    def goto_archive(self):
        if self.app and hasattr(self.app, "show_archive"):
            self.app.show_archive()

    def safe_count(self, fn):
        try:
            return fn()
        except Exception:
            return 0
