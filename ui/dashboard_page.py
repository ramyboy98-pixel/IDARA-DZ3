import os
import customtkinter as ctk

from database import (
    search_archive,
    search_customers,
    count_documents_today,
    count_services_today,
    get_recent_documents,
    get_recent_services,
    get_favorites,
)
from print_manager import open_file


class DashboardPage(ctk.CTkFrame):

    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.build_ui()

    def build_ui(self):

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(4, 18))

        welcome = ctk.CTkFrame(
            top,
            corner_radius=22,
            fg_color="#FFFFFF"
        )
        welcome.pack(fill="x")

        title = ctk.CTkLabel(
            welcome,
            text="IDARA DZ",
            font=("Segoe UI", 28, "bold"),
            text_color="#111827"
        )
        title.pack(anchor="e", padx=26, pady=(20, 6))

        subtitle = ctk.CTkLabel(
            welcome,
            text="برنامج مكتبي لإدارة الوثائق، النماذج، الأرشيف والخدمات الإلكترونية.",
            font=("Segoe UI", 15),
            text_color="#6B7280"
        )
        subtitle.pack(anchor="e", padx=26, pady=(0, 20))

        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", pady=(0, 18))

        archive_count = len(search_archive(""))
        customers_count = len(search_customers(""))
        documents_today = count_documents_today()
        services_today = count_services_today()

        self.stat_card(stats, "📄", "وثائق اليوم", str(documents_today), 0)
        self.stat_card(stats, "🌐", "خدمات اليوم", str(services_today), 1)
        self.stat_card(stats, "🗂️", "الأرشيف", str(archive_count), 2)
        self.stat_card(stats, "👥", "الزبائن", str(customers_count), 3)

        shortcuts = ctk.CTkFrame(self, corner_radius=22, fg_color="#FFFFFF")
        shortcuts.pack(fill="x", pady=(0, 16))

        label = ctk.CTkLabel(
            shortcuts,
            text="اختصارات سريعة",
            font=("Segoe UI", 22, "bold"),
            text_color="#111827"
        )
        label.pack(anchor="e", padx=26, pady=(18, 12))

        grid = ctk.CTkFrame(shortcuts, fg_color="transparent")
        grid.pack(fill="x", padx=22, pady=(0, 18))

        self.shortcut_button(grid, "📄 وثيقة جديدة", self.app.show_documents if self.app else None, 0)
        self.shortcut_button(grid, "🗂️ فتح الأرشيف", self.app.show_archive if self.app else None, 1)
        self.shortcut_button(grid, "🌐 الخدمات الإلكترونية", self.app.show_services if self.app else None, 2)

        lists = ctk.CTkFrame(self, fg_color="transparent")
        lists.pack(fill="both", expand=True)

        lists.grid_columnconfigure(0, weight=1)
        lists.grid_columnconfigure(1, weight=1)
        lists.grid_columnconfigure(2, weight=1)

        self.recent_documents_card(lists, 0)
        self.recent_services_card(lists, 1)
        self.favorites_card(lists, 2)

    def stat_card(self, parent, icon, title, value, col):

        card = ctk.CTkFrame(
            parent,
            height=120,
            corner_radius=22,
            fg_color="#FFFFFF"
        )
        card.grid(row=0, column=col, sticky="nsew", padx=9)
        parent.grid_columnconfigure(col, weight=1)
        card.grid_propagate(False)

        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=("Segoe UI Emoji", 26)
        )
        icon_label.pack(anchor="e", padx=18, pady=(15, 0))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Segoe UI", 22, "bold"),
            text_color="#111827"
        )
        value_label.pack(anchor="e", padx=18)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 14),
            text_color="#6B7280"
        )
        title_label.pack(anchor="e", padx=18)

    def shortcut_button(self, parent, text, command, col):

        btn = ctk.CTkButton(
            parent,
            text=text,
            height=52,
            corner_radius=16,
            font=("Segoe UI", 15, "bold"),
            fg_color="#F3F4F6",
            hover_color="#E5E7EB",
            text_color="#111827",
            command=command
        )
        btn.grid(row=0, column=col, sticky="nsew", padx=10, pady=6)
        parent.grid_columnconfigure(col, weight=1)

    def panel(self, parent, title, col):
        card = ctk.CTkFrame(parent, corner_radius=22, fg_color="#FFFFFF")
        card.grid(row=0, column=col, sticky="nsew", padx=8)
        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 18, "bold"),
            text_color="#111827"
        ).pack(anchor="e", padx=18, pady=(16, 10))
        return card

    def empty_label(self, parent, text):
        ctk.CTkLabel(
            parent,
            text=text,
            font=("Segoe UI", 13),
            text_color="#9CA3AF"
        ).pack(anchor="e", padx=18, pady=(4, 14))

    def item_button(self, parent, text, command=None):
        btn = ctk.CTkButton(
            parent,
            text=text,
            anchor="e",
            height=34,
            corner_radius=10,
            fg_color="#F9FAFB",
            hover_color="#EFF6FF",
            text_color="#111827",
            font=("Segoe UI", 12),
            command=command,
        )
        btn.pack(fill="x", padx=14, pady=4)

    def recent_documents_card(self, parent, col):
        card = self.panel(parent, "آخر الوثائق", col)
        rows = get_recent_documents(5)
        if not rows:
            self.empty_label(card, "لا توجد وثائق حديثة.")
            return

        for _id, customer, phone, document_type, template, word_path, pdf_path, created_at in rows:
            title = template or document_type or "وثيقة"
            subtitle = customer or phone or created_at
            text = f"{title}  —  {subtitle}"
            self.item_button(card, text, lambda path=pdf_path or word_path: open_file(path) if path else None)

    def recent_services_card(self, parent, col):
        card = self.panel(parent, "آخر الخدمات", col)
        rows = get_recent_services(5)
        if not rows:
            self.empty_label(card, "لا توجد خدمات حديثة.")
            return

        for _id, service_name, service_url, customer, phone, notes, created_at in rows:
            text = service_name or service_url or "خدمة"
            self.item_button(card, text, self.app.show_services if self.app else None)

    def favorites_card(self, parent, col):
        card = self.panel(parent, "المفضلة ⭐", col)
        rows = get_favorites(limit=6)
        if not rows:
            self.empty_label(card, "لم تضف عناصر إلى المفضلة بعد.")
            return

        for _id, item_type, item_key, title, subtitle, created_at in rows:
            text = f"⭐ {title or item_key}"
            self.item_button(card, text)
