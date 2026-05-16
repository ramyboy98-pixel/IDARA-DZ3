import webbrowser
import customtkinter as ctk
from tkinter import messagebox

from database import count_services_today, log_service_operation, search_service_operations


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
        header.pack(fill="x", pady=(10, 12))

        title = ctk.CTkLabel(
            header,
            text="🌐 الخدمات الإلكترونية",
            font=("Segoe UI", 30, "bold"),
            text_color="#111827"
        )
        title.pack(anchor="e")

        subtitle = ctk.CTkLabel(
            header,
            text="روابط سريعة للمواقع الرسمية. كل مرة تفتح فيها خدمة يتم تسجيلها ضمن خدمات اليوم.",
            font=("Segoe UI", 14),
            text_color="#6B7280"
        )
        subtitle.pack(anchor="e", pady=(4, 0))

        stats = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=18)
        stats.pack(fill="x", pady=(0, 12))

        self.today_label = ctk.CTkLabel(
            stats,
            text=f"خدمات اليوم: {count_services_today()}",
            font=("Segoe UI", 18, "bold"),
            text_color="#111827"
        )
        self.today_label.pack(side="right", padx=18, pady=16)

        refresh_btn = ctk.CTkButton(
            stats,
            text="تحديث",
            width=90,
            height=34,
            corner_radius=12,
            fg_color="#F3F4F6",
            hover_color="#E5E7EB",
            text_color="#111827",
            command=self.refresh_counter,
        )
        refresh_btn.pack(side="left", padx=18, pady=16)

        search_bar = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E5E7EB")
        search_bar.pack(fill="x", pady=(0, 8))

        self.search_entry = ctk.CTkEntry(
            search_bar,
            placeholder_text="بحث في الخدمات الإلكترونية...",
            width=360,
            height=40,
            corner_radius=14,
            font=("Segoe UI", 14),
            justify="right",
        )
        self.search_entry.pack(side="right", padx=14, pady=12)
        self.search_entry.bind("<KeyRelease>", self.on_search_key)

        clear_btn = ctk.CTkButton(
            search_bar,
            text="مسح",
            width=80,
            height=40,
            corner_radius=14,
            fg_color="#F3F4F6",
            hover_color="#E5E7EB",
            text_color="#111827",
            command=self.clear_search,
        )
        clear_btn.pack(side="left", padx=14, pady=12)

        self.suggestions_box = ctk.CTkFrame(self, fg_color="transparent")
        self.suggestions_box.pack(fill="x", pady=(0, 6))

        self.area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.area.pack(fill="both", expand=True)

        self.cards_grid = ctk.CTkFrame(self.area, fg_color="transparent")
        self.cards_grid.pack(fill="x")
        self.render_service_cards()

        ctk.CTkLabel(
            self.area,
            text="آخر الخدمات المفتوحة",
            font=("Segoe UI", 20, "bold"),
            text_color="#111827"
        ).pack(anchor="e", padx=6, pady=(22, 8))

        self.recent_box = ctk.CTkFrame(self.area, fg_color="transparent")
        self.recent_box.pack(fill="x")
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
        box = ctk.CTkFrame(self.suggestions_box, fg_color="#FFFFFF", corner_radius=14, border_width=1, border_color="#E5E7EB")
        box.pack(fill="x")
        for icon, name, url in matching:
            btn = ctk.CTkButton(
                box, text=f"{icon} {name}", anchor="e", height=32, corner_radius=10,
                fg_color="transparent", hover_color="#EFF6FF", text_color="#111827",
                font=("Segoe UI", 13), command=lambda value=name: self.choose_service_suggestion(value)
            )
            btn.pack(fill="x", padx=8, pady=3)
        for _, service_name, service_url, customer_name, phone, notes, created_at in recent:
            btn = ctk.CTkButton(
                box, text=f"سابقًا: {service_name}", anchor="e", height=32, corner_radius=10,
                fg_color="transparent", hover_color="#EFF6FF", text_color="#111827",
                font=("Segoe UI", 13), command=lambda value=service_name: self.choose_service_suggestion(value)
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
                text_color="#6B7280"
            ).grid(row=0, column=0, sticky="e", padx=10, pady=18)
            return
        for index, (icon, name, url) in enumerate(services):
            row, col = divmod(index, 3)
            self.service_card(self.cards_grid, icon, name, url, row, col)

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
            text="فتح وتسجيل الخدمة",
            width=180,
            height=36,
            command=lambda: self.open_service(name, url)
        )
        btn.pack()

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

        rows = search_service_operations("")[:5]
        if not rows:
            ctk.CTkLabel(
                self.recent_box,
                text="لا توجد خدمات مسجلة بعد.",
                font=("Segoe UI", 14),
                text_color="#6B7280"
            ).pack(anchor="e", padx=12, pady=8)
            return

        for _, service_name, service_url, customer_name, phone, notes, created_at in rows:
            card = ctk.CTkFrame(self.recent_box, fg_color="#FFFFFF", corner_radius=14)
            card.pack(fill="x", pady=5)
            ctk.CTkLabel(
                card,
                text=f"🌐 {service_name}",
                font=("Segoe UI", 15, "bold"),
                text_color="#111827"
            ).pack(anchor="e", padx=14, pady=(10, 2))
            ctk.CTkLabel(
                card,
                text=f"التاريخ: {created_at}",
                font=("Segoe UI", 12),
                text_color="#6B7280"
            ).pack(anchor="e", padx=14, pady=(0, 10))
