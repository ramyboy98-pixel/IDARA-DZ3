import customtkinter as ctk


class SettingsPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.build_ui()

    def build_ui(self):

        card = ctk.CTkFrame(
            self,
            corner_radius=22,
            fg_color="#FFFFFF"
        )
        card.pack(fill="x", pady=10)

        title = ctk.CTkLabel(
            card,
            text="⚙️ الإعدادات",
            font=("Segoe UI", 28, "bold"),
            text_color="#111827"
        )
        title.pack(anchor="e", padx=24, pady=(24, 10))

        text = ctk.CTkLabel(
            card,
            text=(
                "هذه الصفحة مخصصة لاحقا لإعدادات البرنامج:\n"
                "مسارات الحفظ، النسخ الاحتياطي، الثيم، إعدادات الطباعة، وإدارة الروابط."
            ),
            font=("Segoe UI", 15),
            text_color="#6B7280",
            justify="right"
        )
        text.pack(anchor="e", padx=24, pady=(0, 24))
