import customtkinter as ctk


class DocumentsPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.build_ui()

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="📄 قسم الوثائق",
            font=("Segoe UI", 28, "bold")
        )
        title.pack(pady=(20, 40))

        grid = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        grid.pack(expand=True)

        documents = [
            ("📄", "طلب خطي"),
            ("🖋️", "تصريح شرفي"),
            ("📑", "سيرة ذاتية"),
            ("🧾", "فاتورة"),
            ("➕", "أخرى")
        ]

        row = 0
        col = 0

        for icon, name in documents:

            card = ctk.CTkButton(
                grid,
                text=f"{icon}\n\n{name}",
                width=230,
                height=170,
                corner_radius=22,
                font=("Segoe UI", 20, "bold"),
                fg_color="#F3F4F6",
                hover_color="#E5E7EB",
                text_color="#111827",
                command=lambda n=name: self.open_document_form(n)
            )

            card.grid(
                row=row,
                column=col,
                padx=18,
                pady=18
            )

            col += 1

            if col > 2:
                col = 0
                row += 1

    def open_document_form(self, document_name):

        window = ctk.CTkToplevel(self)

        window.title(document_name)
        window.geometry("700x650")

        title = ctk.CTkLabel(
            window,
            text=document_name,
            font=("Segoe UI", 26, "bold")
        )
        title.pack(pady=20)

        form = ctk.CTkFrame(window)
        form.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        fields = [
            "الاسم",
            "اللقب",
            "تاريخ الميلاد",
            "مكان الميلاد",
            "العنوان",
            "رقم الهاتف",
            "الجهة المرسل إليها",
            "الموضوع"
        ]

        self.entries = {}

        for field in fields:

            label = ctk.CTkLabel(
                form,
                text=field,
                anchor="e",
                font=("Segoe UI", 15, "bold")
            )
            label.pack(
                fill="x",
                pady=(12, 5)
            )

            entry = ctk.CTkEntry(
                form,
                height=40,
                font=("Segoe UI", 14)
            )
            entry.pack(fill="x")

            self.entries[field] = entry

        create_btn = ctk.CTkButton(
            form,
            text="📄 إنشاء الوثيقة",
            height=45,
            font=("Segoe UI", 16, "bold"),
            command=lambda: self.generate_document(document_name)
        )
        create_btn.pack(pady=25)

    def generate_document(self, document_name):

        data = {}

        for field, entry in self.entries.items():
            data[field] = entry.get()

        print("نوع الوثيقة:", document_name)
        print(data)
