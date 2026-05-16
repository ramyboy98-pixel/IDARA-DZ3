import customtkinter as ctk
from tkinter import ttk, messagebox

from database import (
    save_customer,
    search_customers
)


class CustomersPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.build_ui()
        self.load_customers()

    def build_ui(self):

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 20))

        title = ctk.CTkLabel(
            header,
            text="ًں‘¥ ط§ظ„ط²ط¨ط§ط¦ظ†",
            font=("Segoe UI", 30, "bold"),
            text_color="#111827"
        )
        title.pack(side="right")

        self.search_entry = ctk.CTkEntry(
            header,
            placeholder_text="ط¨ط­ط« ط¨ط§ط³ظ… ط§ظ„ط²ط¨ظˆظ† ط£ظˆ ط§ظ„ظ‡ط§طھظپ...",
            width=320,
            height=42,
            font=("Segoe UI", 14)
        )
        self.search_entry.pack(side="left", padx=10)

        self.search_entry.bind("<KeyRelease>", lambda e: self.load_customers())

        form = ctk.CTkFrame(
            self,
            corner_radius=22,
            fg_color="#FFFFFF"
        )
        form.pack(fill="x", pady=(0, 20))

        self.first_name = self.create_input(form, "ط§ظ„ط§ط³ظ…")
        self.last_name = self.create_input(form, "ط§ظ„ظ„ظ‚ط¨")
        self.address = self.create_input(form, "ط§ظ„ط¹ظ†ظˆط§ظ†")
        self.phone = self.create_input(form, "ط±ظ‚ظ… ط§ظ„ظ‡ط§طھظپ")

        save_btn = ctk.CTkButton(
            form,
            text="ًں’¾ ط­ظپط¸ ط§ظ„ط²ط¨ظˆظ†",
            height=44,
            font=("Segoe UI", 15, "bold"),
            command=self.save_customer_action
        )
        save_btn.pack(fill="x", padx=20, pady=20)

        table_card = ctk.CTkFrame(
            self,
            corner_radius=22,
            fg_color="#FFFFFF"
        )
        table_card.pack(fill="both", expand=True)

        style = ttk.Style()

        try:
            style.theme_use("default")
        except:
            pass

        style.configure(
            "Treeview",
            rowheight=34,
            font=("Segoe UI", 11),
            background="#FFFFFF",
            fieldbackground="#FFFFFF"
        )

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 11, "bold")
        )

        columns = (
            "first_name",
            "last_name",
            "phone",
            "address"
        )

        self.tree = ttk.Treeview(
            table_card,
            columns=columns,
            show="headings"
        )

        self.tree.heading("first_name", text="ط§ظ„ط§ط³ظ…")
        self.tree.heading("last_name", text="ط§ظ„ظ„ظ‚ط¨")
        self.tree.heading("phone", text="ط§ظ„ظ‡ط§طھظپ")
        self.tree.heading("address", text="ط§ظ„ط¹ظ†ظˆط§ظ†")

        self.tree.column("first_name", width=150, anchor="center")
        self.tree.column("last_name", width=150, anchor="center")
        self.tree.column("phone", width=140, anchor="center")
        self.tree.column("address", width=350, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_card,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(18, 0), pady=18)
        scrollbar.pack(side="right", fill="y", pady=18, padx=(0, 18))

    def create_input(self, parent, label_text):

        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=("Segoe UI", 14, "bold"),
            anchor="e"
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

        if not first_name:
            messagebox.showerror("ط®ط·ط£", "ط§ظƒطھط¨ ط§ط³ظ… ط§ظ„ط²ط¨ظˆظ†")
            return

        save_customer(
            first_name,
            self.last_name.get().strip(),
            self.address.get().strip(),
            self.phone.get().strip()
        )

        self.first_name.delete(0, "end")
        self.last_name.delete(0, "end")
        self.address.delete(0, "end")
        self.phone.delete(0, "end")

        self.load_customers()

    def load_customers(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        keyword = self.search_entry.get().strip()

        customers = search_customers(keyword)

        for customer in customers:

            customer_id, first_name, last_name, address, phone = customer

            self.tree.insert(
                "",
                "end",
                values=(
                    first_name,
                    last_name,
                    phone,
                    address
                )
            )
