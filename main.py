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
            lambda: self.toast("IDARA DZ ط¬ط§ظ‡ط² ظ„ظ„ط¹ظ…ظ„", "info")
        )

        self.bind("<F1>", lambda e: self.show_documents())
        self.bind("<F2>", lambda e: self.focus_global_search())
        self.bind("<Alt-Key-1>", lambda e: self.show_documents())
        self.bind("<Alt-Key-2>", lambda e: self.show_services())
        self.bind("<Alt-Key-3>", lambda e: self.show_archive())
        self.bind("<Control-p>", lambda e: self.show_archive())
        self.bind("<Escape>", lambda e: self.show_dashboard())

    def toast(self, message, kind="success"):
        ToastNotification(self, message, kind)

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
            text="ظ†ط¸ط§ظ… ط§ظ„ظˆط«ط§ط¦ظ‚ ظˆط§ظ„ط®ط¯ظ…ط§طھ",
            font=("Segoe UI", 13),
            text_color="#9CA3AF"
        )
        subtitle.pack(pady=(0, 25))

        self.nav_buttons = {}

        self.add_nav_button("dashboard", "ًںڈ  ط§ظ„ط±ط¦ظٹط³ظٹط©", self.show_dashboard)
        self.add_nav_button("documents", "ًں“„ ظˆط«ط§ط¦ظ‚", self.show_documents)
        self.add_nav_button("services", "ًںŒگ ط®ط¯ظ…ط§طھ ط¥ظ„ظƒطھط±ظˆظ†ظٹط©", self.show_services)
        self.add_nav_button("archive", "ًں—‚ï¸ڈ ط£ط±ط´ظٹظپ", self.show_archive)

        spacer = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        spacer.pack(fill="both", expand=True)

        self.add_nav_button("settings", "âڑ™ï¸ڈ ط§ظ„ط¥ط¹ط¯ط§ط¯ط§طھ", self.show_settings)


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
            text="ط§ظ„ط±ط¦ظٹط³ظٹط©",
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
            placeholder_text="ط¨ط­ط« ط³ط±ظٹط¹ ظپظٹ ط§ظ„ظ†ظ…ط§ط°ط¬ ظˆط§ظ„ط£ط±ط´ظٹظپ ظˆط§ظ„ط²ط¨ط§ط¦ظ†...",
            width=340,
            height=42,
            corner_radius=14,
            font=("Segoe UI", 14),
            justify="right"
        )
        self.global_search.pack(side="right")
        self.global_search.bind("<Return>", lambda e: self.run_global_search())
        self.global_search.bind("<KeyRelease>", self.update_global_suggestions)
        self.global_search.bind("<FocusOut>", lambda e: self.after(180, self.hide_global_suggestions))

        self.global_search_btn = ctk.CTkButton(
            search_box,
            text="ًں”ژ ط¨ط­ط«",
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
        self.global_suggestions_panel = ctk.CTkFrame(
            self.content_wrapper,
            fg_color="#FFFFFF",
            corner_radius=14,
            border_width=1,
            border_color="#E5E7EB",
        )
        self.global_suggestions_visible = False

    def hide_global_suggestions(self):
        if getattr(self, "global_suggestions_visible", False):
            self.global_suggestions_panel.pack_forget()
            self.global_suggestions_visible = False

    def update_global_suggestions(self, event=None):
        if event is not None and getattr(event, "keysym", "") in ("Return", "Escape", "Up", "Down"):
            if getattr(event, "keysym", "") == "Escape":
                self.hide_global_suggestions()
            return
        query = self.global_search.get().strip()
        for widget in self.global_suggestions_panel.winfo_children():
            widget.destroy()
        if len(query) < 1:
            self.hide_global_suggestions()
            return
        try:
            suggestions = get_search_suggestions(query, limit=7)
        except Exception:
            suggestions = []
        if not suggestions:
            self.hide_global_suggestions()
            return
        for item in suggestions:
            title = item.get("title", "")
            kind = item.get("type", "")
            subtitle = item.get("subtitle", "")
            display = f"{title}  ط¢آ·  {kind}"
            if subtitle:
                display += f"  أ¢â‚¬â€‌  {subtitle}"
            btn = ctk.CTkButton(
                self.global_suggestions_panel,
                text=display,
                anchor="e",
                height=34,
                corner_radius=10,
                fg_color="transparent",
                hover_color="#EFF6FF",
                text_color="#111827",
                font=("Segoe UI", 13),
                command=lambda value=title: self.choose_global_suggestion(value),
            )
            btn.pack(fill="x", padx=8, pady=3)
        if not self.global_suggestions_visible:
            self.global_suggestions_panel.pack(fill="x", padx=260, pady=(0, 8))
            self.global_suggestions_visible = True

    def choose_global_suggestion(self, value):
        self.global_search.delete(0, "end")
        self.global_search.insert(0, value)
        self.hide_global_suggestions()
        self.run_global_search()

    def focus_global_search(self):
        self.global_search.focus()

    def run_global_search(self):
        query = self.global_search.get().strip()
        self.hide_global_suggestions()
        if not query:
            self.toast("ط§ظƒطھط¨ ظƒظ„ظ…ط© ظ„ظ„ط¨ط­ط«", "info")
            self.global_search.focus()
            return
        self.show_search_results(query)

    def show_search_results(self, query):
        self.clear_content()
        self.set_active("search", "ظ†طھط§ط¦ط¬ ط§ظ„ط¨ط­ط«")
        page = SearchPage(self.content, query=query, app=self)
        page.pack(fill="both", expand=True)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def set_active(self, key, title):

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
        self.clear_content()
        self.set_active("dashboard", "ط§ظ„ط±ط¦ظٹط³ظٹط©")
        page = DashboardPage(self.content, app=self)
        page.pack(fill="both", expand=True)

    def show_documents(self):
        self.clear_content()
        self.set_active("documents", "ظˆط«ط§ط¦ظ‚")
        page = DocumentsPage(self.content)
        page.pack(fill="both", expand=True)

    def show_services(self):
        self.clear_content()
        self.set_active("services", "ط®ط¯ظ…ط§طھ ط¥ظ„ظƒطھط±ظˆظ†ظٹط©")
        page = ServicesPage(self.content, app=self)
        page.pack(fill="both", expand=True)

    def show_archive(self):
        self.clear_content()
        self.set_active("archive", "ط§ظ„ط£ط±ط´ظٹظپ")
        page = ArchivePage(self.content)
        page.pack(fill="both", expand=True)

    def show_customers(self):
        self.clear_content()
        self.set_active("customers", "ط§ظ„ط²ط¨ط§ط¦ظ†")
        page = CustomersPage(self.content)
        page.pack(fill="both", expand=True)

    def show_settings(self):
        self.clear_content()
        self.set_active("settings", "ط§ظ„ط¥ط¹ط¯ط§ط¯ط§طھ")
        page = SettingsPage(self.content)
        page.pack(fill="both", expand=True)

    def update_clock(self):

        now = datetime.now().strftime("%Y/%m/%d  -  %H:%M:%S")
        self.clock_label.configure(text=now)
        self.after(1000, self.update_clock)


if __name__ == "__main__":
    app = IdaraDZApp()
    app.mainloop()
