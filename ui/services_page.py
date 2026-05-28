import os
import sys
import webbrowser
import customtkinter as ctk
from tkinter import messagebox, Menu
from PIL import Image

from database import (
    count_services_today,
    log_service_operation,
    search_service_operations,
    get_service_links,
    add_service_link,
    update_service_link,
    delete_service_link,
    search_service_links,
    is_favorite,
    toggle_favorite,
)


BG = "#F5F7FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"
BLUE = "#2563EB"
GRAY_BTN = "#F3F4F6"

SERVICE_CARD_SIZE = 178
SERVICE_LOGO_SIZE = 76
SERVICE_NAME_HEIGHT = 52
SERVICE_COLUMNS = 4


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)


STATIC_SERVICES = [
    {"key": "defense", "name": "وزارة الدفاع الوطني", "logo": "assets/services/defense.png"},
    {"key": "foreign_affairs", "name": "وزارة الخارجية", "logo": "assets/services/foreign_affairs.png"},
    {"key": "interior", "name": "وزارة الداخلية", "logo": "assets/services/interior.png"},
    {"key": "justice", "name": "وزارة العدل", "logo": "assets/services/justice.png"},
    {"key": "finance", "name": "وزارة المالية", "logo": "assets/services/finance.png"},
    {"key": "energy_mines", "name": "وزارة الطاقة و المناجم", "logo": "assets/services/energy_mines.png"},
    {"key": "moudjahidine", "name": "وزارة المجاهدين", "logo": "assets/services/moudjahidine.png"},
    {"key": "religious_affairs", "name": "وزارة الشؤون الدينية و الأوقاف", "logo": "assets/services/religious_affairs.png"},
    {"key": "education", "name": "وزارة التربية", "logo": "assets/services/education.png"},
    {"key": "higher_education", "name": "وزارة التعليم العالي", "logo": "assets/services/higher_education.png"},
    {"key": "vocational_training", "name": "وزارة التكوين و التعليم المهنيين", "logo": "assets/services/vocational_training.png"},
    {"key": "culture", "name": "وزارة الثقافة", "logo": "assets/services/culture.png"},
    {"key": "youth_sports", "name": "وزارة الشباب و الرياضة", "logo": "assets/services/youth_sports.png"},
    {"key": "post_telecom", "name": "وزارة البريد و المواصلات", "logo": "assets/services/post_telecom.png"},
    {"key": "solidarity", "name": "وزارة التضامن", "logo": "assets/services/solidarity.png"},
    {"key": "industry", "name": "وزارة الصناعة", "logo": "assets/services/industry.png"},
    {"key": "agriculture", "name": "وزارة الفلاحة", "logo": "assets/services/agriculture.png"},
    {"key": "housing", "name": "وزارة السكن", "logo": "assets/services/housing.png"},
    {"key": "commerce", "name": "وزارة التجارة", "logo": "assets/services/commerce.png"},
    {"key": "communication", "name": "وزارة الاتصال", "logo": "assets/services/communication.png"},
    {"key": "public_works", "name": "وزارة الاشغال العمومية", "logo": "assets/services/public_works.png"},
    {"key": "water_resources", "name": "وزارة الري", "logo": "assets/services/water_resources.png"},
    {"key": "transport", "name": "وزارة النقل", "logo": "assets/services/transport.png"},
    {"key": "tourism", "name": "وزارة السياحة", "logo": "assets/services/tourism.png"},
    {"key": "health", "name": "وزارة الصحة", "logo": "assets/services/health.png"},
    {"key": "labor", "name": "وزارة العمل", "logo": "assets/services/labor.png"},
    {"key": "environment", "name": "وزارة البيئة", "logo": "assets/services/environment.png"},
    {"key": "fishing", "name": "وزارة الصيد البحري", "logo": "assets/services/fishing.png"},
    {"key": "knowledge_economy", "name": "وزارة اقتصاد المعرفة", "logo": "assets/services/knowledge_economy.png"},
    {"key": "algerie_telecom", "name": "اتصالات الجزائر", "logo": "assets/services/algerie_telecom.png"},
    {"key": "algerie_poste", "name": "بريد الجزائر", "logo": "assets/services/algerie_poste.png"},
    {"key": "e_payment", "name": "الدفع الالكتروني", "logo": "assets/services/e_payment.png"},
    {"key": "red_crescent", "name": "الهلال الاحمر الجزائري", "logo": "assets/services/red_crescent.png"},
    {"key": "tramway", "name": "تسيير خطوط الترامواي", "logo": "assets/services/tramway.png"},
    {"key": "elections", "name": "السلطة المستقلة للانتخابات", "logo": "assets/services/elections.png"},
    {"key": "retirement_fund", "name": "الصندوق الوطني للمتقاعدين", "logo": "assets/services/retirement_fund.png"},
    {"key": "cnas", "name": "الضمان الاجتماعي للاجراء", "logo": "assets/services/cnas.png"},
    {"key": "casnos", "name": "الضمان الاجتماعي لغير الاجراء", "logo": "assets/services/casnos.png"},
    {"key": "onefd", "name": "المراسلة ONEFD", "logo": "assets/services/onefd.png"},
    {"key": "anem", "name": "وكالة التشغيل ANEM", "logo": "assets/services/anem.png"},
    {"key": "public_service", "name": "الوظيف العمومي", "logo": "assets/services/public_service.png"},
    {"key": "taxes", "name": "المديرية العامة للضرائب", "logo": "assets/services/taxes.png"},
    {"key": "public_procurement", "name": "الصفقات العمومية", "logo": "assets/services/public_procurement.png"},
]


class ServicesPage(ctk.CTkFrame):
    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.today_label = None
        self.cards_grid = None
        self.links_box = None
        self.search_entry = None
        self.current_service = None
        self.logo_cache = {}
        self.search_after_id = None
        self.render_after_id = None
        self.current_links_cache = None
        self.build_ui()

    def build_ui(self):
        self.show_services_home()

    def clear_page(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_services_home(self):
        self.current_service = None
        self.clear_page()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(6, 12))

        ctk.CTkLabel(header, text="خدمات إلكترونية", font=("Segoe UI", 30, "bold"), text_color=TEXT).pack(anchor="e")
        ctk.CTkLabel(
            header,
            text="اختر الوزارة أو المصلحة للدخول إلى قائمة الروابط الخاصة بها.",
            font=("Segoe UI", 14),
            text_color=MUTED,
        ).pack(anchor="e", pady=(4, 0))

        top_bar = ctk.CTkFrame(self, fg_color=CARD, corner_radius=20, border_width=1, border_color=BORDER)
        top_bar.pack(fill="x", pady=(0, 12), anchor="n")

        self.today_label = ctk.CTkLabel(
            top_bar,
            text=f"خدمات اليوم: {count_services_today()}",
            font=("Segoe UI", 16, "bold"),
            text_color=TEXT,
        )
        self.today_label.pack(side="right", padx=16, pady=14)

        self.search_entry = ctk.CTkEntry(
            top_bar,
            placeholder_text="بحث في الوزارات والمصالح...",
            width=360,
            height=40,
            corner_radius=14,
            font=("Segoe UI", 14),
            justify="right",
        )
        self.search_entry.pack(side="right", padx=10, pady=14)
        self.search_entry.bind("<KeyRelease>", self.schedule_render_service_cards)

        ctk.CTkButton(
            top_bar,
            text="مسح",
            width=75,
            height=38,
            corner_radius=13,
            fg_color=GRAY_BTN,
            hover_color="#E5E7EB",
            text_color=TEXT,
            command=self.clear_search,
        ).pack(side="left", padx=16, pady=14)

        self.cards_grid = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.cards_grid.pack(fill="both", expand=True, anchor="n", pady=(0, 8))
        self.render_service_cards()

    def clear_search(self):
        if self.search_entry:
            self.search_entry.delete(0, "end")
        self.render_service_cards()

    def schedule_render_service_cards(self, event=None):
        if self.search_after_id:
            try:
                self.after_cancel(self.search_after_id)
            except Exception:
                pass
            self.search_after_id = None
        self.search_after_id = self.after(180, self.render_service_cards)

    def service_matches_keyword(self, service, keyword):
        if not keyword:
            return True
        keyword = keyword.strip()
        return keyword in service["name"] or keyword.lower() in service["key"].lower()

    def render_service_cards(self):
        if not self.cards_grid:
            return

        if self.render_after_id:
            try:
                self.after_cancel(self.render_after_id)
            except Exception:
                pass
            self.render_after_id = None

        for widget in self.cards_grid.winfo_children():
            widget.destroy()

        keyword = self.search_entry.get().strip() if self.search_entry else ""
        services = [s for s in STATIC_SERVICES if self.service_matches_keyword(s, keyword)]

        try:
            services.sort(key=lambda s: 0 if is_favorite("service", s["key"]) else 1)
        except Exception:
            pass

        for col in range(SERVICE_COLUMNS):
            self.cards_grid.grid_columnconfigure(
                col,
                weight=0,
                minsize=SERVICE_CARD_SIZE + 24,
                uniform="service_cards_fixed",
            )

        if not services:
            ctk.CTkLabel(
                self.cards_grid,
                text="لا توجد مصلحة مطابقة للبحث.",
                font=("Segoe UI", 15),
                text_color=MUTED,
            ).grid(row=0, column=0, sticky="e", padx=10, pady=18)
            return

        def render_chunk(start_index=0):
            end_index = min(start_index + 8, len(services))
            for index in range(start_index, end_index):
                service = services[index]
                row, col = divmod(index, SERVICE_COLUMNS)
                self.service_card(self.cards_grid, service, row, col)

            if end_index < len(services):
                self.render_after_id = self.after(10, lambda: render_chunk(end_index))
            else:
                self.render_after_id = None

        render_chunk(0)

    def load_logo(self, logo_path):
        if logo_path in self.logo_cache:
            return self.logo_cache[logo_path]

        full_path = resource_path(logo_path)
        if os.path.exists(full_path):
            try:
                image = Image.open(full_path).convert("RGBA")
                image.thumbnail((SERVICE_LOGO_SIZE, SERVICE_LOGO_SIZE), Image.LANCZOS)

                canvas = Image.new("RGBA", (SERVICE_LOGO_SIZE, SERVICE_LOGO_SIZE), (255, 255, 255, 0))
                x = (SERVICE_LOGO_SIZE - image.width) // 2
                y = (SERVICE_LOGO_SIZE - image.height) // 2
                canvas.paste(image, (x, y), image)

                ctk_image = ctk.CTkImage(
                    light_image=canvas,
                    dark_image=canvas,
                    size=(SERVICE_LOGO_SIZE, SERVICE_LOGO_SIZE),
                )
                self.logo_cache[logo_path] = ctk_image
                return ctk_image
            except Exception:
                pass

        self.logo_cache[logo_path] = None
        return None

    def service_card(self, parent, service, row, col):
        card = ctk.CTkFrame(
            parent,
            width=SERVICE_CARD_SIZE,
            height=SERVICE_CARD_SIZE,
            corner_radius=22,
            fg_color=CARD,
            border_width=1,
            border_color=BORDER,
        )
        card.grid(row=row, column=col, padx=12, pady=12, sticky="n")
        card.grid_propagate(False)
        card.pack_propagate(False)

        fav_text = "⭐" if is_favorite("service", service["key"]) else "☆"

        def toggle_service_favorite():
            try:
                new_state = toggle_favorite("service", service["key"], service["name"], "خدمات إلكترونية")
                fav_btn.configure(text="⭐" if new_state else "☆")
            except Exception as exc:
                messagebox.showerror("خطأ", f"تعذر تعديل المفضلة:\n{exc}")

        fav_btn = ctk.CTkButton(
            card,
            text=fav_text,
            width=30,
            height=26,
            corner_radius=9,
            fg_color="transparent",
            hover_color="#FEF3C7",
            text_color="#F59E0B",
            font=("Segoe UI Emoji", 16),
            command=toggle_service_favorite,
        )
        fav_btn.place(x=8, y=8)

        logo_box = ctk.CTkFrame(
            card,
            width=SERVICE_CARD_SIZE,
            height=98,
            fg_color="transparent",
        )
        logo_box.pack(fill="x", pady=(14, 0))
        logo_box.pack_propagate(False)

        logo = self.load_logo(service["logo"])
        if logo:
            logo_label = ctk.CTkLabel(logo_box, image=logo, text="", width=SERVICE_LOGO_SIZE, height=SERVICE_LOGO_SIZE)
        else:
            logo_label = ctk.CTkLabel(
                logo_box,
                text="🌐",
                font=("Segoe UI Emoji", 42),
                text_color=TEXT,
                width=SERVICE_LOGO_SIZE,
                height=SERVICE_LOGO_SIZE,
            )
        logo_label.pack(anchor="center", pady=(8, 0))

        name_box = ctk.CTkFrame(
            card,
            width=SERVICE_CARD_SIZE,
            height=SERVICE_NAME_HEIGHT,
            fg_color="transparent",
        )
        name_box.pack(fill="x", padx=8, pady=(4, 0))
        name_box.pack_propagate(False)

        name_label = ctk.CTkLabel(
            name_box,
            text=service["name"],
            font=("Segoe UI", 14, "bold"),
            text_color=TEXT,
            wraplength=150,
            justify="center",
            width=154,
            height=SERVICE_NAME_HEIGHT,
        )
        name_label.pack(anchor="center")

        def open_card(_event=None):
            self.show_service_links(service)

        def make_clickable(widget):
            try:
                widget.configure(cursor="hand2")
            except Exception:
                pass
            widget.bind("<Button-1>", open_card)

        for widget in (card, logo_box, logo_label, name_box, name_label):
            make_clickable(widget)

        def enter(_event=None):
            card.configure(fg_color="#EFF6FF", border_color=BLUE)
            name_label.configure(text_color=BLUE)

        def leave(_event=None):
            card.configure(fg_color=CARD, border_color=BORDER)
            name_label.configure(text_color=TEXT)

        for widget in (card, logo_box, logo_label, name_box, name_label):
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)

    def show_service_links(self, service):
        self.current_service = service
        self.clear_page()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(6, 12))

        ctk.CTkButton(
            header,
            text="↩ رجوع",
            width=110,
            height=38,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.show_services_home,
        ).pack(side="left")

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="right")
        ctk.CTkLabel(title_box, text=service["name"], font=("Segoe UI", 28, "bold"), text_color=TEXT).pack(anchor="e")
        ctk.CTkLabel(title_box, text="قائمة الروابط الخاصة بهذه المصلحة", font=("Segoe UI", 14), text_color=MUTED).pack(anchor="e", pady=(4, 0))

        toolbar = ctk.CTkFrame(self, fg_color=CARD, corner_radius=20, border_width=1, border_color=BORDER)
        toolbar.pack(fill="x", pady=(0, 12))

        ctk.CTkButton(
            toolbar,
            text="+ إضافة رابط",
            width=170,
            height=40,
            corner_radius=14,
            font=("Segoe UI", 14, "bold"),
            command=lambda: self.open_link_editor(service["key"]),
        ).pack(side="right", padx=16, pady=14)

        ctk.CTkLabel(
            toolbar,
            text="اضغط على الرابط لفتحه. التعديل والحذف بزر الفأرة الأيمن.",
            font=("Segoe UI", 13),
            text_color=MUTED,
        ).pack(side="right", padx=10)

        self.current_links_cache = None
        self.links_box = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.links_box.pack(fill="both", expand=True)
        self.render_links()

    def render_links(self):
        if not self.links_box or not self.current_service:
            return

        for widget in self.links_box.winfo_children():
            widget.destroy()

        if self.current_links_cache is None:
            self.current_links_cache = get_service_links(self.current_service["key"])
        links = self.current_links_cache
        if not links:
            empty = ctk.CTkFrame(self.links_box, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
            empty.pack(fill="x", pady=8)
            ctk.CTkLabel(empty, text="لا توجد روابط بعد.", font=("Segoe UI", 18, "bold"), text_color=TEXT).pack(pady=(20, 6))
            ctk.CTkLabel(empty, text="اضغط على إضافة رابط لإدخال أول رابط.", font=("Segoe UI", 13), text_color=MUTED).pack(pady=(0, 20))
            return

        for link in links:
            self.link_row(link)

    def link_row(self, link):
        link_id, service_key, title, url, notes, created_at, updated_at = link
        row = ctk.CTkFrame(self.links_box, height=72, fg_color=CARD, corner_radius=14, border_width=1, border_color=BORDER)
        row.pack(fill="x", pady=5)
        row.pack_propagate(False)

        fav_key = str(link_id)
        fav_text = "⭐" if is_favorite("service_link", fav_key) else "☆"

        def toggle_link_favorite():
            try:
                new_state = toggle_favorite(
                    "service_link",
                    fav_key,
                    title,
                    self.current_service["name"] if self.current_service else "خدمات إلكترونية"
                )
                fav_btn.configure(text="⭐" if new_state else "☆")
            except Exception as exc:
                messagebox.showerror("خطأ", f"تعذر تعديل المفضلة:\n{exc}")

        fav_btn = ctk.CTkButton(
            row,
            text=fav_text,
            width=32,
            height=32,
            corner_radius=10,
            fg_color="transparent",
            hover_color="#FEF3C7",
            text_color="#F59E0B",
            font=("Segoe UI Emoji", 16),
            command=toggle_link_favorite,
        )
        fav_btn.pack(side="left", padx=(8, 0))

        ctk.CTkLabel(row, text="…", font=("Segoe UI", 22, "bold"), text_color=MUTED).pack(side="left", padx=12)

        text_box = ctk.CTkFrame(row, fg_color="transparent")
        text_box.pack(side="right", fill="both", expand=True, padx=16, pady=8)

        title_label = ctk.CTkLabel(text_box, text=title, font=("Segoe UI", 18, "bold"), text_color=TEXT, anchor="e")
        title_label.pack(fill="x", anchor="e")

        url_label = ctk.CTkLabel(text_box, text=url, font=("Segoe UI", 11), text_color=MUTED, anchor="e")
        url_label.pack(fill="x", anchor="e", pady=(2, 0))

        def open_link(_event=None):
            try:
                log_service_operation(f"{self.current_service['name']} - {title}", url)
                if self.app:
                    self.app.toast("تم تسجيل وفتح الخدمة", "success")
                webbrowser.open(url)
            except Exception as exc:
                messagebox.showerror("خطأ", f"تعذر فتح الرابط:\n{exc}")

        def show_menu(event):
            menu = Menu(self, tearoff=0)
            menu.add_command(label="تعديل", command=lambda: self.open_link_editor(service_key, link))
            menu.add_command(label="حذف", command=lambda: self.confirm_delete_link(link_id))
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        for widget in (row, text_box, title_label, url_label):
            try:
                widget.configure(cursor="hand2")
            except Exception:
                pass
            widget.bind("<Button-1>", open_link)
            widget.bind("<Button-3>", show_menu)

        def enter(_event=None):
            row.configure(fg_color="#EFF6FF", border_color=BLUE)
            title_label.configure(text_color=BLUE)

        def leave(_event=None):
            row.configure(fg_color=CARD, border_color=BORDER)
            title_label.configure(text_color=TEXT)

        for widget in (row, text_box, title_label, url_label):
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)

    def open_link_editor(self, service_key, existing=None):
        is_edit = existing is not None
        window = ctk.CTkToplevel(self)
        window.title("تعديل رابط" if is_edit else "إضافة رابط")
        window.geometry("560x360")
        window.transient(self.winfo_toplevel())
        window.focus_force()
        window.grab_set()

        box = ctk.CTkFrame(window, fg_color=BG)
        box.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(box, text="تعديل رابط" if is_edit else "إضافة رابط", font=("Segoe UI", 22, "bold"), text_color=TEXT).pack(anchor="e", pady=(0, 16))

        title_entry = ctk.CTkEntry(box, height=42, font=("Segoe UI", 14), justify="right", placeholder_text="اسم الرابط")
        title_entry.pack(fill="x", pady=(0, 10))

        url_entry = ctk.CTkEntry(box, height=42, font=("Segoe UI", 14), justify="left", placeholder_text="https://...")
        url_entry.pack(fill="x", pady=(0, 10))

        notes_entry = ctk.CTkEntry(box, height=42, font=("Segoe UI", 14), justify="right", placeholder_text="ملاحظة اختيارية")
        notes_entry.pack(fill="x", pady=(0, 18))

        if existing:
            link_id, _service_key, title, url, notes, _created, _updated = existing
            title_entry.insert(0, title or "")
            url_entry.insert(0, url or "")
            notes_entry.insert(0, notes or "")
        else:
            link_id = None

        def save():
            title = title_entry.get().strip()
            url = url_entry.get().strip()
            notes = notes_entry.get().strip()
            if not title or not url:
                messagebox.showerror("خطأ", "اكتب اسم الرابط والرابط")
                return
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            try:
                if is_edit:
                    update_service_link(link_id, title, url, notes)
                else:
                    add_service_link(service_key, title, url, notes)
                window.destroy()
                self.current_links_cache = None
                self.render_links()
            except Exception as exc:
                messagebox.showerror("خطأ", f"تعذر حفظ الرابط:\n{exc}")

        ctk.CTkButton(box, text="حفظ", height=44, corner_radius=14, font=("Segoe UI", 15, "bold"), command=save).pack(fill="x")

    def confirm_delete_link(self, link_id):
        if not messagebox.askyesno("تأكيد الحذف", "هل تريد حذف هذا الرابط؟"):
            return
        try:
            delete_service_link(link_id)
            self.current_links_cache = None
            self.render_links()
        except Exception as exc:
            messagebox.showerror("خطأ", f"تعذر حذف الرابط:\n{exc}")
