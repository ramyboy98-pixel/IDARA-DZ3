import customtkinter as ctk


class ToastNotification(ctk.CTkFrame):
    def __init__(self, parent, message, kind="success", duration=2500):
        colors = {
            "success": ("#DCFCE7", "#166534"),
            "error": ("#FEE2E2", "#991B1B"),
            "info": ("#DBEAFE", "#1E40AF"),
            "warning": ("#FEF3C7", "#92400E")
        }

        bg, fg = colors.get(kind, colors["info"])

        super().__init__(
            parent,
            fg_color=bg,
            corner_radius=16
        )

        self.place(
            relx=0.02,
            rely=0.92,
            anchor="sw"
        )

        label = ctk.CTkLabel(
            self,
            text=message,
            font=("Segoe UI", 14, "bold"),
            text_color=fg
        )
        label.pack(padx=20, pady=12)

        self.after(duration, self.destroy)


class LoadingOverlay(ctk.CTkFrame):
    def __init__(self, parent, text="جاري المعالجة..."):
        super().__init__(
            parent,
            fg_color="#000000"
        )

        self.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=1
        )

        box = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=22
        )
        box.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        label = ctk.CTkLabel(
            box,
            text=text,
            font=("Segoe UI", 18, "bold"),
            text_color="#111827"
        )
        label.pack(padx=40, pady=(28, 10))

        sub = ctk.CTkLabel(
            box,
            text="يرجى الانتظار قليلا",
            font=("Segoe UI", 13),
            text_color="#6B7280"
        )
        sub.pack(padx=40, pady=(0, 28))
