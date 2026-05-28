import customtkinter as ctk

BG = "#F5F7FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"
BLUE = "#2563EB"


class AboutPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 18))

        ctk.CTkLabel(
            header,
            text="ℹ️ حول البرنامج",
            font=("Segoe UI", 30, "bold"),
            text_color=TEXT,
        ).pack(anchor="e")

        ctk.CTkLabel(
            header,
            text="معلومات البرنامج والمطور.",
            font=("Segoe UI", 14),
            text_color=MUTED,
        ).pack(anchor="e", pady=(5, 0))

        card = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=24,
            border_width=1,
            border_color=BORDER,
        )
        card.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            card,
            text="IDARA DZ",
            font=("Segoe UI", 34, "bold"),
            text_color=BLUE,
        ).pack(anchor="e", padx=28, pady=(28, 8))

        ctk.CTkLabel(
            card,
            text="الإصدار: v1.1",
            font=("Segoe UI", 16, "bold"),
            text_color=TEXT,
        ).pack(anchor="e", padx=28, pady=(0, 10))

        ctk.CTkLabel(
            card,
            text="برنامج مكتبي لإدارة الوثائق الإدارية، النماذج، الأرشيف، والخدمات الإلكترونية.",
            font=("Segoe UI", 15),
            text_color=MUTED,
            justify="right",
            wraplength=760,
        ).pack(anchor="e", padx=28, pady=(0, 24))

        features = ctk.CTkFrame(card, fg_color="#F9FAFB", corner_radius=18)
        features.pack(fill="x", padx=24, pady=(0, 24))

        ctk.CTkLabel(
            features,
            text="الوظائف الأساسية",
            font=("Segoe UI", 20, "bold"),
            text_color=TEXT,
        ).pack(anchor="e", padx=20, pady=(18, 8))

        features_text = (
            "• إنشاء وثائق Word و PDF من قوالب ثابتة\n"
            "• إدارة النماذج والاستمارات\n"
            "• أرشفة الوثائق والبحث داخلها\n"
            "• خدمات إلكترونية وروابط رسمية\n"
            "• مفضلة، آخر العمليات، ونسخ احتياطي تلقائي"
        )

        ctk.CTkLabel(
            features,
            text=features_text,
            font=("Segoe UI", 14),
            text_color=MUTED,
            justify="right",
        ).pack(anchor="e", padx=20, pady=(0, 18))

        developer_card = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=24,
            border_width=1,
            border_color=BORDER,
        )
        developer_card.pack(fill="x")

        ctk.CTkLabel(
            developer_card,
            text="معلومات المطور",
            font=("Segoe UI", 22, "bold"),
            text_color=TEXT,
        ).pack(anchor="e", padx=28, pady=(24, 12))

        info = (
            "المطور: Mohammed BELKEBIR ABDELKARIM\n"
            "Email: iva23605@gmail.com\n"
            "Telegram: @Mohamad_Abdelkarim"
        )

        ctk.CTkLabel(
            developer_card,
            text=info,
            font=("Segoe UI", 15),
            text_color=MUTED,
            justify="right",
        ).pack(anchor="e", padx=28, pady=(0, 24))
