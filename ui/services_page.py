import os
import shutil
import webbrowser
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

from database import (
    count_services_today,
    log_service_operation,
    search_service_operations,
    get_service_entities,
    get_service_entity,
    add_service_entity,
    update_service_entity,
    delete_service_entity,
    get_service_links,
    add_service_link,
    update_service_link,
    delete_service_link,
)
from utils.paths import get_data_dir


BG = "#F5F7FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"
BLUE = "#2563EB"
GREEN = "#059669"
RED = "#DC2626"
ORANGE = "#F59E0B"


class ServicesPage(ctk.CTkFrame):
    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.mode = "entities"
        self.current_entity_id = None
        self.current_entity_name = ""
        self.today_label = None
        self.cards_grid = None
        self.links_box = None
        self.search_entry = None
        self.logo_cache = {}
        self.build_ui()

    def build_ui(self):
        self.render_entities_page()

    def clear_page(self):
        for widget in self.winfo_children():
            widget.destroy()

    def render_entities_page(self):
        self.mode = "entities"
        self.current_entity_id = None
        self.current_entity_name = ""
        self.clear_page()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 14))

        ctk.CTkLabel(
            header,
            text="الخدمات الإلكترونية",
            font=("Segoe UI", 30, "bold"),
            text_color=TEXT,
        ).pack(anchor="e")

        ctk.CTkLabel(
            header,
            text="اختر المصلحة أو الوزارة للدخول إلى قائمة الروابط الخاصة بها.",
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
            placeholder_text="بحث في المصالح والوزارات...",
            width=360,
            height=40,
            corner_radius=14,
            font=("Segoe UI", 14),
            justify="right",
        )
        self.search_entry.pack(side="right", padx=10, pady=14)
        self.search_entry.bind("<KeyRelease>", lambda _e=None: self.render_entity_cards())

        add_btn = ctk.CTkButton(
            top_bar,
            text="+ إضافة مصلحة",
            width=150,
            height=38,
            corner_radius=13,
            fg_color=BLUE,
            hover_color="#1D4ED8",
            font=("Segoe UI", 14, "bold"),
            command=self.open_entity_form,
        )
        add_btn.pack(side="left", padx=16, pady=14)

        self.cards_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_grid.pack(fill="x", expand=False, anchor="n")
        self.render_entity_cards()

    def render_entity_cards(self):
        if not self.cards_grid:
            return

        for widget in self.cards_grid.winfo_children():
            widget.destroy()

        keyword = self.search_entry.get().strip() if self.search_entry else ""
        entities = get_service_entities(keyword)

        if not entities:
            ctk.CTkLabel(
                self.cards_grid,
                text="لا توجد مصالح مطابقة للبحث.",
                font=("Segoe UI", 15),
                text_color=MUTED,
            ).grid(row=0, column=0, sticky="e", padx=10, pady=18)
            return

        for col in range(4):
            self.cards_grid.grid_columnconfigure(col, weight=1, uniform="service_entity_cards")

        for index, (entity_id, name, logo_path, links_count) in enumerate(entities):
            row, col = divmod(index, 4)
            self.entity_card(self.cards_grid, entity_id, name, logo_path, links_count, row, col)

    def entity_card(self, parent, entity_id, name, logo_path, links_count, row, col):
        card = ctk.CTkFrame(parent, width=220, height=220, corner_radius=18, fg_color=CARD, border_width=1, border_color=BORDER)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="n")
        card.grid_propagate(False)

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=10, pady=(8, 0))

        edit_btn = ctk.CTkButton(
            actions,
            text="✏️",
            width=34,
            height=28,
            corner_radius=10,
            fg_color="#F3F4F6",
            hover_color="#E5E7EB",
            text_color=TEXT,
            command=lambda: self.open_entity_form(entity_id),
        )
        edit_btn.pack(side="left", padx=(0, 4))

        delete_btn = ctk.CTkButton(
            actions,
            text="🗑️",
            width=34,
            height=28,
            corner_radius=10,
            fg_color="#FEE2E2",
            hover_color="#FECACA",
            text_color=RED,
            command=lambda: self.confirm_delete_entity(entity_id, name),
        )
        delete_btn.pack(side="left")

        logo_widget = self.make_logo_widget(card, logo_path, size=82)
        logo_widget.pack(pady=(16, 12))

        name_label = ctk.CTkLabel(
            card,
            text=name,
            font=("Segoe UI", 18, "bold"),
            text_color=TEXT,
            wraplength=185,
            justify="center",
        )
        name_label.pack(pady=(0, 4))

        count_label = ctk.CTkLabel(
            card,
            text=f"{links_count} روابط",
            font=("Segoe UI", 12),
            text_color=MUTED,
        )
        count_label.pack()

        def open_card(_event=None):
            self.render_links_page(entity_id)

        def make_clickable(widget):
            try:
                widget.configure(cursor="hand2")
            except Exception:
                pass
            widget.bind("<Button-1>", open_card)

        for widget in (card, logo_widget, name_label, count_label):
            make_clickable(widget)

        def enter(_event=None):
            card.configure(fg_color="#EFF6FF", border_color=BLUE)
            name_label.configure(text_color=BLUE)

        def leave(_event=None):
            card.configure(fg_color=CARD, border_color=BORDER)
            name_label.configure(text_color=TEXT)

        for widget in (card, logo_widget, name_label, count_label):
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)

    def make_logo_widget(self, parent, logo_path, size=82):
        logo_path = (logo_path or "").strip()
        if logo_path and os.path.exists(logo_path):
            try:
                cache_key = f"{logo_path}:{size}"
                if cache_key not in self.logo_cache:
                    image = Image.open(logo_path)
                    self.logo_cache[cache_key] = ctk.CTkImage(light_image=image, dark_image=image, size=(size, size))
                return ctk.CTkLabel(parent, text="", image=self.logo_cache[cache_key])
            except Exception:
                pass

        return ctk.CTkLabel(parent, text="🏛️", font=("Segoe UI Emoji", 58), text_color=TEXT)

    def render_links_page(self, entity_id):
        entity = get_service_entity(entity_id)
        if not entity:
            messagebox.showerror("خطأ", "هذه المصلحة غير موجودة.")
            self.render_entities_page()
            return

        self.mode = "links"
        self.current_entity_id = entity_id
        self.current_entity_name = entity[1]
        self.clear_page()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 14))

        back_btn = ctk.CTkButton(
            header,
            text="رجوع ←",
            width=115,
            height=38,
            corner_radius=12,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.render_entities_page,
        )
        back_btn.pack(side="left")

        ctk.CTkLabel(
            header,
            text=self.current_entity_name,
            font=("Segoe UI", 30, "bold"),
            text_color=TEXT,
        ).pack(anchor="e")

        ctk.CTkLabel(
            header,
            text="قائمة الروابط الخاصة بهذه المصلحة. اضغط على الرابط لفتحه وتسجيله ضمن خدمات اليوم.",
            font=("Segoe UI", 14),
            text_color=MUTED,
        ).pack(anchor="e", pady=(4, 0))

        top_bar = ctk.CTkFrame(self, fg_color=CARD, corner_radius=20, border_width=1, border_color=BORDER)
        top_bar.pack(fill="x", pady=(0, 12), anchor="n")

        self.search_entry = ctk.CTkEntry(
            top_bar,
            placeholder_text="بحث في روابط هذه المصلحة...",
            width=380,
            height=40,
            corner_radius=14,
            font=("Segoe UI", 14),
            justify="right",
        )
        self.search_entry.pack(side="right", padx=16, pady=14)
        self.search_entry.bind("<KeyRelease>", lambda _e=None: self.render_links_list())

        add_link_btn = ctk.CTkButton(
            top_bar,
            text="+ إضافة رابط",
            width=140,
            height=38,
            corner_radius=13,
            fg_color=BLUE,
            hover_color="#1D4ED8",
            font=("Segoe UI", 14, "bold"),
            command=self.open_link_form,
        )
        add_link_btn.pack(side="left", padx=16, pady=14)

        self.links_box = ctk.CTkFrame(self, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
        self.links_box.pack(fill="x", expand=False, anchor="n")
        self.render_links_list()

    def render_links_list(self):
        if not self.links_box or not self.current_entity_id:
            return

        for widget in self.links_box.winfo_children():
            widget.destroy()

        keyword = self.search_entry.get().strip() if self.search_entry else ""
        links = get_service_links(self.current_entity_id, keyword)

        if not links:
            ctk.CTkLabel(
                self.links_box,
                text="لا توجد روابط في هذه المصلحة.",
                font=("Segoe UI", 15),
                text_color=MUTED,
            ).pack(anchor="e", padx=18, pady=18)
            return

        for link in links:
            self.link_row(self.links_box, link)

    def link_row(self, parent, link):
        link_id, entity_id, title, url, description, created_at, updated_at = link

        row = ctk.CTkFrame(parent, fg_color="transparent", height=74)
        row.pack(fill="x", padx=10, pady=(8, 0))
        row.pack_propagate(False)

        icon_holder = ctk.CTkFrame(row, fg_color="transparent", width=62)
        icon_holder.pack(side="right", fill="y")
        icon_holder.pack_propagate(False)

        entity = get_service_entity(entity_id)
        logo_path = entity[2] if entity else ""
        logo = self.make_logo_widget(icon_holder, logo_path, size=48)
        logo.pack(expand=True)

        text_box = ctk.CTkFrame(row, fg_color="transparent")
        text_box.pack(side="right", fill="both", expand=True, padx=(0, 10))

        title_label = ctk.CTkLabel(
            text_box,
            text=title,
            font=("Segoe UI", 18, "bold"),
            text_color=TEXT,
            anchor="e",
            justify="right",
        )
        title_label.pack(anchor="e")

        small_text = description if description else url
        ctk.CTkLabel(
            text_box,
            text=small_text,
            font=("Segoe UI", 12),
            text_color=MUTED,
            anchor="e",
            justify="right",
        ).pack(anchor="e", pady=(2, 0))

        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.pack(side="left", padx=(8, 0))

        edit_btn = ctk.CTkButton(
            actions,
            text="✏️",
            width=38,
            height=32,
            corner_radius=10,
            fg_color="#F3F4F6",
            hover_color="#E5E7EB",
            text_color=TEXT,
            command=lambda: self.open_link_form(link_id),
        )
        edit_btn.pack(side="left", padx=3)

        del_btn = ctk.CTkButton(
            actions,
            text="🗑️",
            width=38,
            height=32,
            corner_radius=10,
            fg_color="#FEE2E2",
            hover_color="#FECACA",
            text_color=RED,
            command=lambda: self.confirm_delete_link(link_id, title),
        )
        del_btn.pack(side="left", padx=3)

        separator = ctk.CTkFrame(parent, fg_color=BORDER, height=1)
        separator.pack(fill="x", padx=14, pady=(8, 0))

        def open_link(_event=None):
            self.open_service_link(title, url)

        for widget in (row, icon_holder, logo, text_box, title_label):
            try:
                widget.configure(cursor="hand2")
            except Exception:
                pass
            widget.bind("<Button-1>", open_link)

    def open_service_link(self, title, url):
        try:
            log_service_operation(title, url)
            if self.app:
                self.app.toast(f"تم تسجيل خدمة: {title}", "success")
            webbrowser.open(url)
        except Exception as exc:
            messagebox.showerror("خطأ", f"تعذر فتح الرابط:\n{exc}")

    def copy_logo_to_data(self, source_path):
        source_path = (source_path or "").strip()
        if not source_path:
            return ""

        logos_dir = os.path.join(get_data_dir(), "service_logos")
        os.makedirs(logos_dir, exist_ok=True)

        base, ext = os.path.splitext(os.path.basename(source_path))
        safe_base = "".join(ch for ch in base if ch.isalnum() or ch in ("_", "-")) or "logo"
        target = os.path.join(logos_dir, f"{safe_base}_{int(os.path.getmtime(source_path))}{ext}")
        shutil.copy2(source_path, target)
        return target

    def open_entity_form(self, entity_id=None):
        current = get_service_entity(entity_id) if entity_id else None
        selected_logo = {"path": current[2] if current else ""}

        dialog = ctk.CTkToplevel(self)
        dialog.title("تعديل مصلحة" if entity_id else "إضافة مصلحة")
        dialog.geometry("520x360")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=BG)

        frame = ctk.CTkFrame(dialog, fg_color=CARD, corner_radius=18)
        frame.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(
            frame,
            text="تعديل مصلحة" if entity_id else "إضافة مصلحة",
            font=("Segoe UI", 22, "bold"),
            text_color=TEXT,
        ).pack(anchor="e", padx=18, pady=(18, 10))

        name_entry = ctk.CTkEntry(frame, height=42, corner_radius=12, justify="right", font=("Segoe UI", 14))
        name_entry.pack(fill="x", padx=18, pady=8)
        name_entry.insert(0, current[1] if current else "")

        logo_label = ctk.CTkLabel(
            frame,
            text=os.path.basename(selected_logo["path"]) if selected_logo["path"] else "لم يتم اختيار شعار",
            font=("Segoe UI", 13),
            text_color=MUTED,
        )
        logo_label.pack(anchor="e", padx=18, pady=(8, 4))

        def choose_logo():
            path = filedialog.askopenfilename(
                title="اختيار شعار",
                filetypes=[
                    ("صور", "*.png *.jpg *.jpeg *.webp"),
                    ("كل الملفات", "*.*"),
                ],
            )
            if path:
                selected_logo["path"] = path
                logo_label.configure(text=os.path.basename(path))

        ctk.CTkButton(
            frame,
            text="اختيار شعار من الجهاز",
            height=38,
            corner_radius=12,
            fg_color="#F3F4F6",
            hover_color="#E5E7EB",
            text_color=TEXT,
            command=choose_logo,
        ).pack(fill="x", padx=18, pady=8)

        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("خطأ", "اكتب اسم المصلحة.")
                return

            logo_path = selected_logo["path"]
            if logo_path and os.path.exists(logo_path) and not logo_path.startswith(get_data_dir()):
                logo_path = self.copy_logo_to_data(logo_path)

            try:
                if entity_id:
                    update_service_entity(entity_id, name, logo_path)
                else:
                    add_service_entity(name, logo_path)
                dialog.destroy()
                self.logo_cache.clear()
                self.render_entities_page()
            except Exception as exc:
                messagebox.showerror("خطأ", f"تعذر حفظ المصلحة:\n{exc}")

        ctk.CTkButton(
            frame,
            text="حفظ",
            height=42,
            corner_radius=12,
            fg_color=GREEN,
            hover_color="#047857",
            font=("Segoe UI", 15, "bold"),
            command=save,
        ).pack(fill="x", padx=18, pady=(18, 8))

    def confirm_delete_entity(self, entity_id, name):
        if not messagebox.askyesno("تأكيد الحذف", f"هل تريد حذف {name} وكل روابطها؟"):
            return
        try:
            delete_service_entity(entity_id)
            self.render_entities_page()
        except Exception as exc:
            messagebox.showerror("خطأ", f"تعذر حذف المصلحة:\n{exc}")

    def open_link_form(self, link_id=None):
        current = None
        if link_id:
            links = get_service_links(self.current_entity_id)
            for link in links:
                if link[0] == link_id:
                    current = link
                    break

        dialog = ctk.CTkToplevel(self)
        dialog.title("تعديل رابط" if link_id else "إضافة رابط")
        dialog.geometry("560x420")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=BG)

        frame = ctk.CTkFrame(dialog, fg_color=CARD, corner_radius=18)
        frame.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(
            frame,
            text="تعديل رابط" if link_id else "إضافة رابط",
            font=("Segoe UI", 22, "bold"),
            text_color=TEXT,
        ).pack(anchor="e", padx=18, pady=(18, 10))

        title_entry = ctk.CTkEntry(frame, height=42, corner_radius=12, justify="right", font=("Segoe UI", 14), placeholder_text="اسم الخدمة")
        title_entry.pack(fill="x", padx=18, pady=7)
        title_entry.insert(0, current[2] if current else "")

        url_entry = ctk.CTkEntry(frame, height=42, corner_radius=12, justify="left", font=("Segoe UI", 14), placeholder_text="https://...")
        url_entry.pack(fill="x", padx=18, pady=7)
        url_entry.insert(0, current[3] if current else "")

        desc_entry = ctk.CTkEntry(frame, height=42, corner_radius=12, justify="right", font=("Segoe UI", 14), placeholder_text="وصف اختياري")
        desc_entry.pack(fill="x", padx=18, pady=7)
        desc_entry.insert(0, current[4] if current else "")

        def save():
            title = title_entry.get().strip()
            url = url_entry.get().strip()
            desc = desc_entry.get().strip()

            if not title or not url:
                messagebox.showerror("خطأ", "اكتب اسم الخدمة والرابط.")
                return

            try:
                if link_id:
                    update_service_link(link_id, title, url, desc)
                else:
                    add_service_link(self.current_entity_id, title, url, desc)
                dialog.destroy()
                self.render_links_list()
            except Exception as exc:
                messagebox.showerror("خطأ", f"تعذر حفظ الرابط:\n{exc}")

        ctk.CTkButton(
            frame,
            text="حفظ",
            height=42,
            corner_radius=12,
            fg_color=GREEN,
            hover_color="#047857",
            font=("Segoe UI", 15, "bold"),
            command=save,
        ).pack(fill="x", padx=18, pady=(18, 8))

    def confirm_delete_link(self, link_id, title):
        if not messagebox.askyesno("تأكيد الحذف", f"هل تريد حذف الرابط: {title}؟"):
            return
        try:
            delete_service_link(link_id)
            self.render_links_list()
        except Exception as exc:
            messagebox.showerror("خطأ", f"تعذر حذف الرابط:\n{exc}")
