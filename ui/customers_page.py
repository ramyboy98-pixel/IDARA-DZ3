import customtkinter as ctk
from tkinter import messagebox

from database import (
    save_customer,
    search_customers
)


class CustomersPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.build_ui()

    def build_ui(self):

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.pack(fill="x", pady=(10, 20))

        title = ctk.CTkLabel(
            header,
            text="👥 الزبائن",
            font=("Segoe UI", 30, "bold"),
            text_color="#111827"
        )
        title.pack(side="right")

        self.search_entry = ctk.CTkEntry(
            header,
            placeholder_text="بحث باسم الزبون أو الهاتف...",
            width=320,
            height=40,
            font=("Segoe UI", 14)
        )
        self.search_entry.pack(side="left", padx=10)

        search_btn = ctk.CTkButton(
            header,
            text="بحث",
            width=90,
            height=40,
            command=self.load_customers
        )
        search_btn.pack(side="left")

        form = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=22
        )
        form.pack(fill="x", padx=10, pady=(0, 20))

        self.first_name = self.create_input(form, "الاسم")
        self.last_name = self.create_input(form, "اللقب")
        self.address = self.create_input(form, "العنوان")
        self.phone = self.create_input(form, "رقم الهاتف")

        save_btn = ctk.CTkButton(
            form,
            text="💾 حفظ الزبون",
            height=42,
            command=self.save_customer_action
        )
        save_btn.pack(fill="x", padx=20, pady=20)

        self.results = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.results.pack(fill="both", expand=True)

        self.load_customers()

    def create_input(self, parent, label_text):

        label = ctk.CTkLabel(
            parent,
            text=label_text,
            anchor="e",
            font=("Segoe UI", 14, "bold"),
            text_color="#111827"
        )
        label.pack(fill="x", padx=20, pady=(14, 5))

        entry = ctk.CTkEntry(
            parent,
            height=40,
            font=("Segoe UI", 14)
        )
        entry.pack(fill="x", padx=20)

        return entry

    def save_customer_action(self):

        first_name = self.first_name.get().strip()
        last_name = self.last_name.get().strip()
        address = self.address.get().strip()
        phone = self.phone.get().strip()

        if not first_name:
            messagebox.showerror("خطأ", "اكتب اسم الزبون")
            return

        save_customer(first_name, last_name, address, phone)

        self.first_name.delete(0, "end")
        self.last_name.delete(0, "end")
        self.address.delete(0, "end")
        self.phone.delete(0, "end")

        self.load_customers()

    def load_customers(self):

        for widget in self.results.winfo_children():
            widget.destroy()

        keyword = self.search_entry.get().strip()
        customers = search_customers(keyword)

        if not customers:
            empty = ctk.CTkLabel(
                self.results,
                text="لا توجد بيانات.",
                font=("Segoe UI", 18),
                text_color="#6B7280"
            )
            empty.pack(pady=80)
            return

        for customer in customers:

            customer_id, first_name, last_name, address, phone = customer

            card = ctk.CTkFrame(
                self.results,
                corner_radius=18,
                fg_color="#FFFFFF"
            )
            card.pack(fill="x", padx=10, pady=10)

            info = ctk.CTkLabel(
                card,
                text=(
                    f"👤 {first_name} {last_name}\n"
                    f"📞 {phone}\n"
                    f"📍 {address}"
                ),
                justify="right",
                anchor="e",
                font=("Segoe UI", 15),
                text_color="#111827"
            )

            info.pack(fill="x", padx=20, pady=20)
