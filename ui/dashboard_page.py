import customtkinter as ctk

from database import search_archive, search_customers


class DashboardPage(ctk.CTkFrame):

    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.build_ui()

    def build_ui(self):

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 22))

        welcome = ctk.CTkFrame(
            top,
            corner_radius=22,
            fg_color="#FFFFFF"
        )
        welcome.pack(fill="x")

        title = ctk.CTkLabel(
            welcome,
            text="مرحبا بك في IDARA DZ",
            font=("Segoe UI", 26, "bold"),
            text_color="#111827"
        )
        title.pack(anchor="e", padx=24, pady=(22, 6))

        subtitle = ctk.CTkLabel(
            welcome,
            text="برنامج مكتبي لإدارة الوثائق، النماذج، الزبائن، الأرشيف والخدمات الإلكترونية.",
            font=("Segoe UI", 15),
            text_color="#6B7280"
        )
        subtitle.pack(anchor="e", padx=24, pady=(0, 22))

        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", pady=(0, 22))

        archive_count = len(search_archive(""))
        customers_count = len(search_customers(""))

        self.stat_card(stats, "🗂️", "الأرشيف", str(archive_count), 0)
        self.stat_card(stats, "👥", "الزبائن", str(customers_count), 1)
        self.stat_card(stats, "📄", "وثائق", "ديناميكي", 2)
        self.stat_card(stats, "🌐", "خدمات", "جاهز", 3)

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
        label.pack(anchor="e", padx=24, pady=(22, 18))

        grid = ctk.CTkFrame(shortcuts, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=10)

        self.shortcut_button(grid, "📄 وثيقة جديدة", self.app.show_documents if self.app else None, 0)
        self.shortcut_button(grid, "🗂️ فتح الأرشيف", self.app.show_archive if self.app else None, 1)
        self.shortcut_button(grid, "👥 إدارة الزبائن", self.app.show_customers if self.app else None, 2)
        self.shortcut_button(grid, "🌐 الخدمات الإلكترونية", self.app.show_services if self.app else None, 3)

    def stat_card(self, parent, icon, title, value, col):

        card = ctk.CTkFrame(
            parent,
            height=130,
            corner_radius=22,
            fg_color="#FFFFFF"
        )
        card.grid(row=0, column=col, sticky="nsew", padx=8)
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
        btn.grid(row=0, column=col, sticky="nsew", padx=8, pady=10)
        parent.grid_columnconfigure(col, weight=1)
