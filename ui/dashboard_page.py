import customtkinter as ctk
from datetime import datetime

from database import (
    search_archive,
    search_customers,
    count_documents_today,
    count_services_today,
)


class DashboardPage(ctk.CTkFrame):

    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.build_ui()

    def build_ui(self):

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(4, 24))

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
        title.pack(anchor="e", padx=26, pady=(22, 6))

        subtitle = ctk.CTkLabel(
            welcome,
            text="برنامج مكتبي لإدارة الوثائق، النماذج، الأرشيف والخدمات الإلكترونية.",
            font=("Segoe UI", 15),
            text_color="#6B7280"
        )
        subtitle.pack(anchor="e", padx=26, pady=(0, 22))

        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", pady=(0, 24))

        archive_count = len(search_archive(""))
        customers_count = len(search_customers(""))
        documents_today = count_documents_today()
        services_today = count_services_today()

        self.stat_card(stats, "📄", "وثائق اليوم", str(documents_today), 0)
        self.stat_card(stats, "🌐", "خدمات اليوم", str(services_today), 1)
        self.stat_card(stats, "🗂️", "الأرشيف", str(archive_count), 2)
        self.stat_card(stats, "👥", "الزبائن", str(customers_count), 3)

        shortcuts = ctk.CTkFrame(
            self,
            corner_radius=22,
            fg_color="#FFFFFF"
        )
        shortcuts.pack(fill="both", expand=True)

        label = ctk.CTkLabel(
            shortcuts,
            text="اختصارات سريعة",
            font=("Segoe UI", 22, "bold"),
            text_color="#111827"
        )
        label.pack(anchor="e", padx=26, pady=(22, 18))

        grid = ctk.CTkFrame(shortcuts, fg_color="transparent")
        grid.pack(fill="x", padx=22, pady=10)

        self.shortcut_button(grid, "📄 وثيقة جديدة", self.app.show_documents if self.app else None, 0)
        self.shortcut_button(grid, "🗂️ فتح الأرشيف", self.app.show_archive if self.app else None, 1)
        self.shortcut_button(grid, "🌐 الخدمات الإلكترونية", self.app.show_services if self.app else None, 2)

    def stat_card(self, parent, icon, title, value, col):

        card = ctk.CTkFrame(
            parent,
            height=130,
            corner_radius=22,
            fg_color="#FFFFFF"
        )
        card.grid(row=0, column=col, sticky="nsew", padx=9)
        parent.grid_columnconfigure(col, weight=1)
        card.grid_propagate(False)

        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=("Segoe UI Emoji", 28)
        )
        icon_label.pack(anchor="e", padx=18, pady=(18, 0))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Segoe UI", 23, "bold"),
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
            height=58,
            corner_radius=16,
            font=("Segoe UI", 16, "bold"),
            fg_color="#F3F4F6",
            hover_color="#E5E7EB",
            text_color="#111827",
            command=command
        )
        btn.grid(row=0, column=col, sticky="nsew", padx=10, pady=10)
        parent.grid_columnconfigure(col, weight=1)
