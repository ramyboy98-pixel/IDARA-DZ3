import customtkinter as ctk


class SplashScreen(ctk.CTkToplevel):

    def __init__(self, parent, duration=1200):
        super().__init__(parent)

        self.duration = duration

        self.overrideredirect(True)
        self.geometry("520x300")
        self.configure(fg_color="#111827")

        self.center_window()

        title = ctk.CTkLabel(
            self,
            text="IDARA DZ",
            font=("Segoe UI", 36, "bold"),
            text_color="white"
        )
        title.pack(pady=(70, 8))

        subtitle = ctk.CTkLabel(
            self,
            text="ï؟½ï؟½ï؟½ï؟½ ï؟½ï؟½ï؟½ï؟½ï؟½ï؟½ï؟½ ï؟½ï؟½ï؟½ï؟½ï؟½ï؟½ï؟½ï؟½ ï؟½ï؟½ï؟½ï؟½ï؟½ï؟½ï؟½ï؟½ï؟½ï؟½ï؟½",
            font=("Segoe UI", 15),
            text_color="#D1D5DB"
        )
        subtitle.pack(pady=(0, 35))

        loading = ctk.CTkLabel(
            self,
            text="ï؟½ï؟½ï؟½ï؟½ ï؟½ï؟½ï؟½ï؟½ï؟½ï؟½ï؟½...",
            font=("Segoe UI", 14),
            text_color="#93C5FD"
        )
        loading.pack()

        self.after(self.duration, self.destroy)

    def center_window(self):
        self.update_idletasks()

        width = 520
        height = 300

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))

        self.geometry(f"{width}x{height}+{x}+{y}")
