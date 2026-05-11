import webbrowser
import customtkinter as ctk


class ServicesPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.build_ui()

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="🌐 الخدمات الإلكترونية",
            font=("Segoe UI", 30, "bold"),
            text_color="#111827"
        )
        title.pack(anchor="e", pady=(10, 8))

        subtitle = ctk.CTkLabel(
            self,
            text="روابط سريعة للخدمات والمواقع الرسمية. يمكن تطويرها لاحقا لإضافة وحذف الروابط من داخل البرنامج.",
            font=("Segoe UI", 14),
            text_color="#6B7280"
        )
        subtitle.pack(anchor="e", pady=(0, 22))

        self.area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.area.pack(fill="both", expand=True)

        services = [
            ("🏛️", "وزارة الداخلية", "https://www.interieur.gov.dz"),
            ("💼", "الوظيف العمومي", "https://www.concours-fonction-publique.gov.dz"),
            ("🎓", "وزارة التعليم العالي", "https://www.mesrs.dz"),
            ("🏥", "الضمان الاجتماعي", "https://www.cnas.dz"),
            ("💰", "الضرائب", "https://www.mfdgi.gov.dz"),
            ("📬", "بريد الجزائر", "https://www.poste.dz"),
        ]

        grid = ctk.CTkFrame(self.area, fg_color="transparent")
        grid.pack(fill="x")

        row = 0
        col = 0

        for icon, name, url in services:
            self.service_card(grid, icon, name, url, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def service_card(self, parent, icon, name, url, row, col):

        card = ctk.CTkFrame(
            parent,
            width=280,
            height=160,
            corner_radius=22,
            fg_color="#FFFFFF"
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_propagate(False)
        parent.grid_columnconfigure(col, weight=1)

        label = ctk.CTkLabel(
            card,
            text=f"{icon}\n{name}",
            font=("Segoe UI", 19, "bold"),
            text_color="#111827"
        )
        label.pack(pady=(22, 10))

        btn = ctk.CTkButton(
            card,
            text="فتح الموقع",
            width=160,
            height=36,
            command=lambda: webbrowser.open(url)
        )
        btn.pack()
