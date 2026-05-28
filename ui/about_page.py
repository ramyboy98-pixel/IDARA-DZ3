# -*- coding: utf-8 -*-
import customtkinter as ctk


BG = "#F5F7FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"
BLUE = "#2563EB"


class AboutPage(ctk.CTkFrame):
    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(6, 12))

        ctk.CTkLabel(
            header,
            text="حول البرنامج",
            font=("Segoe UI", 30, "bold"),
            text_color=TEXT,
        ).pack(anchor="e")

        ctk.CTkLabel(
            header,
            text="معلومات البرنامج والمطور",
            font=("Segoe UI", 14),
            text_color=MUTED,
        ).pack(anchor="e", pady=(4, 0))

        # مهم: جعل الصفحة قابلة للتمرير حتى لا تختفي المعلومات السفلية
        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#CBD5E1",
            scrollbar_button_hover_color="#94A3B8",
        )
        scroll.pack(fill="both", expand=True, padx=0, pady=(0, 8))

        main_card = ctk.CTkFrame(
            scroll,
            fg_color=CARD,
            corner_radius=24,
            border_width=1,
            border_color=BORDER,
        )
        main_card.pack(fill="x", padx=4, pady=(0, 16))

        ctk.CTkLabel(
            main_card,
            text="IDARA DZ",
            font=("Segoe UI", 34, "bold"),
            text_color=BLUE,
        ).pack(anchor="center", pady=(30, 6))

        ctk.CTkLabel(
            main_card,
            text="الإصدار: v1.1",
            font=("Segoe UI", 16, "bold"),
            text_color=TEXT,
        ).pack(anchor="center", pady=(0, 14))

        ctk.CTkLabel(
            main_card,
            text="برنامج مكتبي لإدارة الوثائق الإدارية، النماذج، الأرشيف، والخدمات الإلكترونية.",
            font=("Segoe UI", 15),
            text_color=MUTED,
            wraplength=780,
            justify="center",
        ).pack(anchor="center", padx=30, pady=(0, 28))

        self.section(
            scroll,
            title="الوظائف الأساسية",
            lines=[
                "صناعة وثائق Word و PDF انطلاقًا من نماذج Word.",
                "إدارة النماذج والاستمارات.",
                "أرشفة الوثائق والبحث داخلها.",
                "خدمات إلكترونية وروابط رسمية منظمة حسب الوزارة أو المصلحة.",
                "مفضلة، آخر العمليات، ونسخ احتياطي تلقائي.",
            ],
        )

        self.section(
            scroll,
            title="اختصارات لوحة المفاتيح",
            lines=[
                "F1: فتح قسم الوثائق.",
                "F2 أو Ctrl+F: التركيز على البحث.",
                "F3 أو Ctrl+P: فتح الأرشيف.",
                "F4: فتح الخدمات الإلكترونية.",
                "F5 أو Esc: العودة إلى الرئيسية.",
                "F6: فتح الإعدادات.",
                "F7: فتح صفحة حول البرنامج.",
            ],
        )

        self.section(
            scroll,
            title="معلومات المطور",
            lines=[
                "المطور: Mohammed BELKEBIR ABDELKARIM",
                "Email: iva23605@gmail.com",
                "Telegram: @Mohamad_Abdelkarim",
            ],
        )

        self.section(
            scroll,
            title="ملاحظات",
            lines=[
                "هذا البرنامج موجّه لتسهيل العمل اليومي في إدارة الوثائق والخدمات الإلكترونية.",
                "يُنصح بالاحتفاظ بنسخ احتياطية من قاعدة البيانات بشكل دوري.",
                "يمكن تطوير البرنامج لاحقًا بإضافة روابط وخدمات ونماذج جديدة.",
            ],
        )

        footer = ctk.CTkFrame(scroll, fg_color="transparent")
        footer.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            footer,
            text="IDARA DZ © 2026",
            font=("Segoe UI", 13),
            text_color=MUTED,
        ).pack(anchor="center")

    def section(self, parent, title, lines):
        card = ctk.CTkFrame(
            parent,
            fg_color=CARD,
            corner_radius=20,
            border_width=1,
            border_color=BORDER,
        )
        card.pack(fill="x", padx=4, pady=8)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 20, "bold"),
            text_color=TEXT,
        ).pack(anchor="e", padx=22, pady=(18, 8))

        for line in lines:
            ctk.CTkLabel(
                card,
                text="• " + line,
                font=("Segoe UI", 14),
                text_color=MUTED,
                anchor="e",
                justify="right",
                wraplength=820,
            ).pack(fill="x", anchor="e", padx=26, pady=3)

        ctk.CTkFrame(card, height=10, fg_color="transparent").pack()
