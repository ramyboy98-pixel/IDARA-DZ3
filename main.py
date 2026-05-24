# -*- coding: utf-8 -*-
import customtkinter as ctk
from datetime import datetime

from database import init_database, get_search_suggestions
from ui.dashboard_page import DashboardPage
from ui.documents_page import DocumentsPage
from ui.archive_page import ArchivePage
from ui.customers_page import CustomersPage
from ui.services_page import ServicesPage
from ui.settings_page import SettingsPage
from ui.search_page import SearchPage
from ui.splash_screen import SplashScreen
from ui.ux_widgets import ToastNotification

APP_NAME = "IDARA DZ"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class IdaraDZApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        init_database()

        self.title(APP_NAME)
        self.geometry("1250x780")
        self.minsize(1050, 680)

        self.current_page = None

        self.build_ui()
        self.show_dashboard()
        self.update_clock()

        SplashScreen(self)

        self.after(
            1300,
            lambda: self.toast("مرحبا بك في IDARA DZ", "info")
        )

        self.bind("<F1>", lambda e: self.show_documents())
        self.bind("<F2>", lambda e: self.focus_global_search())
        self.bind("<Alt-Key-1>", lambda e: self.show_documents())
        self.bind("<Alt-Key-2>", lambda e: self.show_services())
        self.bind("<Alt-Key-3>", lambda e: self.show_archive())
        self.bind("<Control-p>", lambda e: self.show_archive())
        self.bind("<Escape>", lambda e: self.show_dashboard())

    def toast(self, message, kind="success"):
        """عرض إشعار مؤقت"""
        try:
            ToastNotification(self, message, kind)
        except Exception as e:
            print(f"خطأ في عرض الإشعار: {e}")

    def build_ui(self):

        self.configure(fg_color="#F5F7FA")

        self.root_frame = ctk.CTkFrame(
            self,
            fg_color="#F5F7FA"
        )
        self.root_frame.pack(fill="both", expand=True)

        self.sidebar = ctk.CTkFrame(
            self.root_frame,
            width=235,
            corner_radius=0,
            fg_color="#111827"
        )
        self.sidebar.pack(side="right", fill="y")
        self.sidebar.pack_propagate(False)

        self.content_wrapper = ctk.CTkFrame(
            self.root_frame,
            fg_color="#F5F7FA"
        )
        self.content_wrapper.pack(side="left", fill="both", expand=True)

        self.build_sidebar()
        self.build_topbar()
        self.build_global_suggestions_panel()

        self.content = ctk.CTkFrame(
            self.content_wrapper,
            fg_color="#F5F7FA"
        )
        self.content.pack(fill="both", expand=True, padx=24, pady=(8, 24))

    def build_sidebar(self):

        logo = ctk.CTkLabel(
            self.sidebar,
            text="IDARA DZ",
            font=("Segoe UI", 28, "bold"),
            text_color="white"
        )
        logo.pack(pady=(28, 2))

        subtitle = ctk.CTkLabel(
            self.sidebar,
            text="نظام الوثائق والخدمات",
            font=("Segoe UI", 13),
            text_color="#9CA3AF"
        )
        subtitle.pack(pady=(0, 25))

        self.nav_buttons = {}

        self.add_nav_button("dashboard", "📊 الرئيسية", self.show_dashboard)
        self.add_nav_button("documents", "📄 وثائق", self.show_documents)
        self.add_nav_button("services", "🔧 خدمات إلكترونية", self.show_services)
        self.add_nav_button("archive", "📁 أرشيف", self.show_archive)

        spacer = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        spacer.pack(fill="both", expand=True)

        self.add_nav_button("settings", "⚙️ الإعدادات", self.show_settings)


    def add_nav_button(self, key, text, command):

        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            height=44,
            corner_radius=12,
            font=("Segoe UI", 15, "bold"),
            anchor="e",
            fg_color="transparent",
            hover_color="#1F2937",
            text_color="#E5E7EB",
            command=command
        )

        btn.pack(fill="x", padx=16, pady=5)

        self.nav_buttons[key] = btn

    def build_topbar(self):

        self.topbar = ctk.CTkFrame(
            self.content_wrapper,
            height=74,
            fg_color="#F5F7FA"
        )
        self.topbar.pack(fill="x", padx=24, pady=(18, 0))
        self.topbar.pack_propagate(False)

        self.page_title = ctk.CTkLabel(
            self.topbar,
            text="الرئيسية",
            font=("Segoe UI", 26, "bold"),
            text_color="#111827"
        )
        self.page_title.pack(side="right", padx=4)

        self.clock_label = ctk.CTkLabel(
            self.topbar,
            text="",
            font=("Segoe UI", 13),
            text_color="#6B7280"
        )
        self.clock_label.pack(side="left", padx=6)

        search_box = ctk.CTkFrame(self.topbar, fg_color="transparent")
        search_box.pack(side="left", padx=14)

        self.global_search = ctk.CTkEntry(
            search_box,
            placeholder_text="بحث سريع في النماذج والأرشيف والزبائن...",
            width=340,
            height=42,
            corner_radius=14,
            font=("Segoe UI", 14),
            justify="right"
        )
        self.global_search.pack(side="right")
        self.global_search.bind("<Return>", lambda e: self.run_global_search())
        self.global_search.bind("<KeyRelease>", self.update_global_suggestions)
        self.global_search.bind("<FocusOut>", lambda e: self.after(220, self.hide_global_suggestions))

        self.global_search_btn = ctk.CTkButton(
            search_box,
            text="🔍 بحث",
            width=78,
            height=42,
            corner_radius=14,
            font=("Segoe UI", 13, "bold"),
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color="#111827",
            command=self.run_global_search,
        )
        self.global_search_btn.pack(side="right", padx=(8, 0))


    def build_global_suggestions_panel(self):
        # نافذة عائمة حقيقية، لا تأخذ أي مساحة داخل الصفحة
        self.global_suggestions_window = None
        self.global_suggestions_visible = False

    def hide_global_suggestions(self):
        if getattr(self, "global_suggestions_window", None) is not None:
            try:
                self.global_suggestions_window.destroy()
            except Exception:
                pass
        self.global_suggestions_window = None
        self.global_suggestions_visible = False

    def update_global_suggestions(self, event=None):
        """تحديث قائمة اقتراحات البحث الذكية"""
        if event is not None and getattr(event, "keysym", "") in ("Return", "Escape", "Up", "Down"):
            if getattr(event, "keysym", "") == "Escape":
                self.hide_global_suggestions()
            return

        query = self.global_search.get().strip()

        if len(query) < 1:
            self.hide_global_suggestions()
            return

        try:
            suggestions = get_search_suggestions(query, limit=3)
        except Exception as e:
            print(f"خطأ في الحصول على الاقتراحات: {e}")
            suggestions = []

        if not suggestions:
            self.hide_global_suggestions()
            return

        self.show_global_suggestions_dropdown(suggestions[:3])

    def show_global_suggestions_dropdown(self, suggestions):
        """عرض الاقتراحات كقائمة صغيرة تحت خانة البحث مباشرة"""
        self.hide_global_suggestions()
        self.update_idletasks()

        entry_x = self.global_search.winfo_rootx()
        entry_y = self.global_search.winfo_rooty() + self.global_search.winfo_height() + 2
        entry_w = self.global_search.winfo_width() or 340

        dropdown_h = (len(suggestions) * 32) + 10

        win = ctk.CTkToplevel(self)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.geometry(f"{entry_w}x{dropdown_h}+{entry_x}+{entry_y}")
        win.configure(fg_color="#E5E5E5")

        panel = ctk.CTkFrame(
            win,
            fg_color="#E5E5E5",
            corner_radius=0,
            border_width=0
        )
        panel.pack(fill="both", expand=True)

        for item in suggestions:
            title = str(item.get("title", "") or "").strip()
            kind = str(item.get("type", "") or "").strip()
            subtitle = str(item.get("subtitle", "") or "").strip()

            if not title:
                continue

            display = title
            if kind:
                display = f"{title}    {kind}"

            btn = ctk.CTkButton(
                panel,
                text=display,
                anchor="e",
                height=28,
                corner_radius=0,
                fg_color="#E5E5E5",
                hover_color="#D6D6D6",
                text_color="#111827",
                font=("Segoe UI", 12),
                command=lambda value=title: self.choose_global_suggestion(value),
            )
            btn.pack(fill="x", padx=0, pady=0)

        self.global_suggestions_window = win
        self.global_suggestions_visible = True

    def choose_global_suggestion(self, value):
        """اختيار اقتراح"""
        try:
            self.global_search.delete(0, "end")
            self.global_search.insert(0, value)
            self.hide_global_suggestions()
            self.run_global_search()
        except Exception as e:
            print(f"خطأ في اختيار الاقتراح: {e}")

    def focus_global_search(self):
        """التركيز على حقل البحث"""
        self.global_search.focus()

    def run_global_search(self):
        """تنفيذ البحث العام"""
        query = self.global_search.get().strip()
        self.hide_global_suggestions()

        if not query:
            self.toast("اكتب كلمة للبحث", "info")
            self.global_search.focus()
            return

        self.show_search_results(query)

    def show_search_results(self, query):
        """عرض نتائج البحث"""
        try:
            self.clear_content()
            self.set_active("search", "نتائج البحث")
            page = SearchPage(self.content, query=query, app=self)
            page.pack(fill="both", expand=True)
        except Exception as e:
            print(f"خطأ في عرض نتائج البحث: {e}")
            self.toast(f"خطأ: {str(e)}", "error")

    def clear_content(self):
        """مسح محتوى الصفحة الحالية"""
        for widget in self.content.winfo_children():
            widget.destroy()

    def set_active(self, key, title):
        """تعيين الصفحة النشطة"""
        self.current_page = key
        self.page_title.configure(text=title)

        for name, button in self.nav_buttons.items():
            if name == key:
                button.configure(
                    fg_color="#2563EB",
                    hover_color="#1D4ED8",
                    text_color="white"
                )
            else:
                button.configure(
                    fg_color="transparent",
                    hover_color="#1F2937",
                    text_color="#E5E7EB"
                )

    def show_dashboard(self):
        """عرض صفحة لوحة التحكم"""
        try:
            self.clear_content()
            self.set_active("dashboard", "الرئيسية")
            page = DashboardPage(self.content, app=self)
            page.pack(fill="both", expand=True)
        except Exception as e:
            print(f"خطأ في عرض لوحة التحكم: {e}")
            self.toast(f"خطأ: {str(e)}", "error")

    def show_documents(self):
        """عرض صفحة الوثائق"""
        try:
            self.clear_content()
            self.set_active("documents", "وثائق")
            page = DocumentsPage(self.content)
            page.pack(fill="both", expand=True)
        except Exception as e:
            print(f"خطأ في عرض الوثائق: {e}")
            self.toast(f"خطأ: {str(e)}", "error")

    def show_services(self):
        """عرض صفحة الخدمات"""
        try:
            self.clear_content()
            self.set_active("services", "خدمات إلكترونية")
            page = ServicesPage(self.content, app=self)
            page.pack(fill="both", expand=True)
        except Exception as e:
            print(f"خطأ في عرض الخدمات: {e}")
            self.toast(f"خطأ: {str(e)}", "error")

    def show_archive(self):
        """عرض صفحة الأرشيف"""
        try:
            self.clear_content()
            self.set_active("archive", "الأرشيف")
            page = ArchivePage(self.content)
            page.pack(fill="both", expand=True)
        except Exception as e:
            print(f"خطأ في عرض الأرشيف: {e}")
            self.toast(f"خطأ: {str(e)}", "error")

    def show_customers(self):
        """عرض صفحة الزبائن"""
        try:
            self.clear_content()
            self.set_active("customers", "الزبائن")
            page = CustomersPage(self.content)
            page.pack(fill="both", expand=True)
        except Exception as e:
            print(f"خطأ في عرض الزبائن: {e}")
            self.toast(f"خطأ: {str(e)}", "error")

    def show_settings(self):
        """عرض صفحة الإعدادات"""
        try:
            self.clear_content()
            self.set_active("settings", "الإعدادات")
            page = SettingsPage(self.content)
            page.pack(fill="both", expand=True)
        except Exception as e:
            print(f"خطأ في عرض الإعدادات: {e}")
            self.toast(f"خطأ: {str(e)}", "error")

    def update_clock(self):
        """تحديث الساعة"""
        try:
            now = datetime.now().strftime("%Y/%m/%d  -  %H:%M:%S")
            self.clock_label.configure(text=now)
        except Exception as e:
            print(f"خطأ في تحديث الساعة: {e}")
        finally:
            self.after(1000, self.update_clock)


if __name__ == "__main__":
    app = IdaraDZApp()
    app.mainloop()
