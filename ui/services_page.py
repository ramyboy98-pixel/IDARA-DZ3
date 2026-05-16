import webbrowser
import customtkinter as ctk
from tkinter import messagebox

from database import count_services_today, log_service_operation, search_service_operations


BG = "#F5F7FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"
BLUE = "#2563EB"

SERVICES = [
    ("🏛️", "وزارة الداخلية", "https://www.interieur.gov.dz"),
    ("💼", "الوظيف العمومي", "https://www.concours-fonction-publique.gov.dz"),
    ("🎓", "وزارة التعليم العالي", "https://www.mesrs.dz"),
    ("🏥", "الضمان الاجتماعي", "https://www.cnas.dz"),
    ("💰", "الضرائب", "https://www.mfdgi.gov.dz"),
    ("📬", "بريد الجزائر", "https://www.poste.dz"),
]


class ServicesPage(ctk.CTkFrame):
    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.today_label = None
        self.recent_box = None
        self.cards_grid = None
        self.search_entry = None
        self.suggestions_box = None
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 14))

        ctk.CTkLabel(
            header,
            text="🌐 الخدمات الإلكترونية",
            font=("Segoe UI", 30, "bold"),
            text_color=TEXT,
        ).pack(anchor="e")

        ctk.CTkLabel(
            header,
            text="روابط سريعة للمواقع الرسمية. اضغط على البطاقة لفتح الخدمة وتسجيلها ضمن خدمات اليوم.",
            font=("Segoe UI", 14),
            text_color=MUTED,
        ).pack(anchor="e", pady=(4, 0))

        top_bar = ctk.CTkFrame(self, fg_color=CARD, corner_radius=20, border_width=1, border_color=BORDER)
        top_bar.pack(fill="x", pady=(0, 12), anchor="n")

        self.today_label = ctk.CTkLabel(
            top_bar,
            text=f"خدمات اليوم: {count_services_today()}",
            font=("Segoe UI", 17, "bold"),
            text_color=TEXT,
        )
        self.today_label.pack(side="right", padx=16, pady=14)

        self.search_entry = ctk.CTkEntry(
            top_bar,
            placeholder_text="بحث في الخدمات الإلكترونية...",
            width=360,
            height=40,
            corner_radius=14,
            font=("Segoe UI", 14),
            justify="right",
        )
        self.search_entry.pack(side="right", padx=10, pady=14)
        self.search_entry.bind("<KeyRelease>", self.on_search_key)

        clear_btn = ctk.CTkButton(
            top_bar,
            text="مسح",
            width=75,
            height=38,
            corner_radius=13,
            fg_color="#F3F4F6",
            hover_color="#E5E7EB",
            text_color=TEXT,
            command=self.clear_search,
        )
        clear_btn.pack(side="left", padx=16, pady=14)

        self.suggestions_box = ctk.CTkFrame(self, fg_color="transparent")
        self.suggestions_box.pack(fill="x", pady=(0, 6), anchor="n")

        # لا نستعمل إطار تمرير داخلي هنا حتى لا تختفي البطاقات في الأسفل.
        self.cards_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_grid.pack(fill="x", expand=False, anchor="n", pady=(0, 14))
        self.render_service_cards()

        recent_title = ctk.CTkLabel(
            self,
            text="آخر الخدمات المفتوحة",
            font=("Segoe UI", 19, "bold"),
            text_color=TEXT,
        )
        recent_title.pack(anchor="e", pady=(4, 8))

        self.recent_box = ctk.CTkFrame(self, fg_color="transparent")
        self.recent_box.pack(fill="x", expand=False, anchor="n")
        self.refresh_recent()

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.clear_suggestions()
        self.render_service_cards()

    def on_search_key(self, event=None):
        self.load_service_suggestions()
        self.render_service_cards()

    def clear_suggestions(self):
        if self.suggestions_box:
            for widget in self.suggestions_box.winfo_children():
                widget.destroy()

    def load_service_suggestions(self):
        self.clear_suggestions()
        keyword = self.search_entry.get().strip()
        if not keyword:
            return
        matching = [s for s in SERVICES if keyword in s[1] or keyword in s[2]][:6]
        recent = search_service_operations(keyword)[:4]
        if not matching and not recent:
            return
        box = ctk.CTkFrame(self.suggestions_box, fg_color=CARD, corner_radius=14, border_width=1, border_color=BORDER)
        box.pack(fill="x")
        for icon, name, url in matching:
            btn = ctk.CTkButton(
                box,
                text=f"{icon} {name}",
                anchor="e",
                height=32,
                corner_radius=10,
                fg_color="transparent",
                hover_color="#EFF6FF",
                text_color=TEXT,
                font=("Segoe UI", 13),
                command=lambda value=name: self.choose_service_suggestion(value),
            )
            btn.pack(fill="x", padx=8, pady=3)
        for _, service_name, service_url, customer_name, phone, notes, created_at in recent:
            btn = ctk.CTkButton(
                box,
                text=f"سابقًا: {service_name}",
                anchor="e",
                height=32,
                corner_radius=10,
                fg_color="transparent",
                hover_color="#EFF6FF",
                text_color=TEXT,
                font=("Segoe UI", 13),
                command=lambda value=service_name: self.choose_service_suggestion(value),
            )
            btn.pack(fill="x", padx=8, pady=3)

    def choose_service_suggestion(self, value):
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, value)
        self.clear_suggestions()
        self.render_service_cards()

    def render_service_cards(self):
        if not self.cards_grid:
            return
        for widget in self.cards_grid.winfo_children():
            widget.destroy()
        keyword = self.search_entry.get().strip() if self.search_entry else ""
        services = [s for s in SERVICES if not keyword or keyword in s[1] or keyword in s[2]]
        if not services:
            ctk.CTkLabel(
                self.cards_grid,
                text="لا توجد خدمة مطابقة للبحث.",
                font=("Segoe UI", 15),
                text_color=MUTED,
            ).grid(row=0, column=0, sticky="e", padx=10, pady=18)
            return
        for col in range(3):
            self.cards_grid.grid_columnconfigure(col, weight=1, uniform="service_cards")
        for index, (icon, name, url) in enumerate(services):
            row, col = divmod(index, 3)
            self.service_card(self.cards_grid, icon, name, url, row, col)

    def service_card(self, parent, icon, name, url, row, col):
        card = ctk.CTkFrame(parent, width=280, height=135, corner_radius=20, fg_color=CARD, border_width=1, border_color=BORDER)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        card.grid_propagate(False)

        icon_label = ctk.CTkLabel(card, text=icon, font=("Segoe UI Emoji", 30), text_color=TEXT)
        icon_label.pack(pady=(18, 4))

        name_label = ctk.CTkLabel(card, text=name, font=("Segoe UI", 17, "bold"), text_color=TEXT)
        name_label.pack(pady=(0, 3))

        hint_label = ctk.CTkLabel(card, text="اضغط للفتح والتسجيل", font=("Segoe UI", 11), text_color=MUTED)
        hint_label.pack()

        def open_card(_event=None):
            self.open_service(name, url)

        def make_clickable(widget):
            try:
                widget.configure(cursor="hand2")
            except Exception:
                pass
            widget.bind("<Button-1>", open_card)

        for widget in (card, icon_label, name_label, hint_label):
            make_clickable(widget)

        def enter(_event=None):
            card.configure(fg_color="#EFF6FF", border_color=BLUE)
            icon_label.configure(text_color=BLUE)
            name_label.configure(text_color=BLUE)

        def leave(_event=None):
            card.configure(fg_color=CARD, border_color=BORDER)
            icon_label.configure(text_color=TEXT)
            name_label.configure(text_color=TEXT)

        for widget in (card, icon_label, name_label, hint_label):
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)

    def open_service(self, name, url):
        try:
            log_service_operation(name, url)
            self.refresh_counter()
            self.refresh_recent()
            if self.app:
                self.app.toast(f"تم تسجيل خدمة: {name}", "success")
            webbrowser.open(url)
        except Exception as exc:
            messagebox.showerror("خطأ", f"تعذر تسجيل أو فتح الخدمة:\n{exc}")

    def refresh_counter(self):
        if self.today_label:
            self.today_label.configure(text=f"خدمات اليوم: {count_services_today()}")

    def refresh_recent(self):
        if not self.recent_box:
            return
        for widget in self.recent_box.winfo_children():
            widget.destroy()

        rows = search_service_operations("")[:3]
        if not rows:
            ctk.CTkLabel(
                self.recent_box,
                text="لا توجد خدمات مسجلة بعد.",
                font=("Segoe UI", 14),
                text_color=MUTED,
            ).pack(anchor="e", padx=12, pady=8)
            return

        for _, service_name, service_url, customer_name, phone, notes, created_at in rows:
            card = ctk.CTkFrame(self.recent_box, fg_color=CARD, corner_radius=14, border_width=1, border_color=BORDER)
            card.pack(fill="x", pady=4)
            ctk.CTkLabel(
                card,
                text=f"🌐 {service_name}",
                font=("Segoe UI", 14, "bold"),
                text_color=TEXT,
            ).pack(anchor="e", padx=14, pady=(8, 1))
            ctk.CTkLabel(
                card,
                text=f"التاريخ: {created_at}",
                font=("Segoe UI", 11),
                text_color=MUTED,
            ).pack(anchor="e", padx=14, pady=(0, 8))
