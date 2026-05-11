import customtkinter as ctk
from datetime import datetime
from ui.documents_page import DocumentsPage

APP_NAME = "IDARA DZ"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class IdaraDZApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1200x750")
        self.minsize(1000, 650)

        self.dark_mode = False

        self.build_ui()
        self.update_clock()

        self.bind("<F1>", lambda e: self.open_documents())
        self.bind("<F2>", lambda e: self.search_entry.focus())
        self.bind("<Alt-Key-1>", lambda e: self.open_documents())
        self.bind("<Alt-Key-2>", lambda e: self.open_services())
        self.bind("<Alt-Key-3>", lambda e: self.open_archive())
        self.bind("<Escape>", lambda e: self.show_home())

    def build_ui(self):

        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        self.build_header()

        self.search_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="بحث سريع...",
            height=45,
            font=("Segoe UI", 15),
            corner_radius=14
        )
        self.search_entry.pack(
            fill="x",
            pady=(35, 20)
        )

        self.content = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.content.pack(
            fill="both",
            expand=True
        )

        self.show_home()

    def build_header(self):

        self.header = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.header.pack(fill="x")

        self.logo_label = ctk.CTkLabel(
            self.header,
            text="IDARA DZ",
            font=("Segoe UI", 30, "bold"),
            text_color="#111827"
        )
        self.logo_label.pack(side="left")

        self.clock_label = ctk.CTkLabel(
            self.header,
            text="",
            font=("Segoe UI", 14),
            text_color="#374151"
        )
        self.clock_label.pack(side="right", padx=10)

        self.settings_btn = ctk.CTkButton(
            self.header,
            text="⚙️ الإعدادات",
            width=120,
            height=36,
            command=self.open_settings
        )
        self.settings_btn.pack(side="right", padx=10)

        self.dark_btn = ctk.CTkButton(
            self.header,
            text="🌙 الوضع الداكن",
            width=140,
            height=36,
            command=self.toggle_dark_mode
        )
        self.dark_btn.pack(side="right", padx=10)

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    def show_home(self):

        self.clear_content()

        title = ctk.CTkLabel(
            self.content,
            text="الواجهة الرئيسية",
            font=("Segoe UI", 24, "bold")
        )
        title.pack(
            pady=(25, 35)
        )

        cards_frame = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )
        cards_frame.pack(expand=True)

        self.create_card(
            cards_frame,
            "📄",
            "وثائق",
            "استخراج الوثائق الإدارية",
            self.open_documents,
            0
        )

        self.create_card(
            cards_frame,
            "🌐",
            "خدمات إلكترونية",
            "روابط وخدمات رسمية",
            self.open_services,
            1
        )

        self.create_card(
            cards_frame,
            "🗂️",
            "أرشيف",
            "حفظ وبحث وإعادة طباعة",
            self.open_archive,
            2
        )

    def create_card(
        self,
        parent,
        icon,
        title,
        subtitle,
        command,
        column
    ):

        card = ctk.CTkButton(
            parent,
            text=f"{icon}\n\n{title}\n{subtitle}",
            font=("Segoe UI", 19, "bold"),
            width=280,
            height=230,
            corner_radius=22,
            fg_color="#F3F4F6",
            hover_color="#E5E7EB",
            text_color="#111827",
            command=command
        )

        card.grid(
            row=0,
            column=column,
            padx=25,
            pady=20
        )

    def page_title(self, text):

        label = ctk.CTkLabel(
            self.content,
            text=text,
            font=("Segoe UI", 26, "bold")
        )
        label.pack(pady=30)

    def open_documents(self):

        self.clear_content()

        page = DocumentsPage(self.content)
        page.pack(fill="both", expand=True)

    def open_services(self):

        self.clear_content()

        self.page_title("🌐 قسم الخدمات الإلكترونية")

    def open_archive(self):

        self.clear_content()

        self.page_title("🗂️ قسم الأرشيف")

    def open_settings(self):

        self.clear_content()

        self.page_title("⚙️ الإعدادات")

    def toggle_dark_mode(self):

        self.dark_mode = not self.dark_mode

        if self.dark_mode:

            ctk.set_appearance_mode("dark")

            self.dark_btn.configure(
                text="☀️ الوضع الفاتح"
            )

        else:

            ctk.set_appearance_mode("light")

            self.dark_btn.configure(
                text="🌙 الوضع الداكن"
            )

    def update_clock(self):

        now = datetime.now().strftime(
            "%Y/%m/%d  -  %H:%M:%S"
        )

        self.clock_label.configure(
            text=now
        )

        self.after(
            1000,
            self.update_clock
        )


if __name__ == "__main__":

    app = IdaraDZApp()
    app.mainloop()
