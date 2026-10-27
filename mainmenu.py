import customtkinter as ctk

class MainMenuPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_login, app_controller):
        super().__init__(parent, fg_color=app_controller.current_palette["bg"])
        self.switch_to_login = switch_to_login
        self.app = app_controller
        p = self.app.current_palette

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # ==========================================
        # 1. SOL MENÜ (SIDEBAR)
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=p["sidebar"])
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="🎓 SAÜ Connect",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=p["text_main"]
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 25), sticky="w")

        self.sidebar_buttons = []
        self.btn_notes = self.create_sidebar_button("📚 Ders Notları", 1, self.open_notes)
        self.btn_polls = self.create_sidebar_button("📊 Anketler", 2, self.open_polls)
        self.btn_events = self.create_sidebar_button("🎉 Kampüs Etkinlikleri", 3, self.open_events)
        self.btn_settings = self.create_sidebar_button("⚙️ Ayarlar", 4, self.open_settings)

        self.logout_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="🚪 Çıkış Yap",
            fg_color="#F38BA8",
            hover_color="#EBA0AC",
            text_color="#11111B",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            corner_radius=8,
            command=self.switch_to_login
        )
        self.logout_btn.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

        # ==========================================
        # 2. SAĞ ANA İÇERİK ALANI
        # ==========================================
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)

        self.welcome_title = ctk.CTkLabel(
            self.header_frame,
            text="Hoş Geldiniz 👋",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=p["text_main"]
        )
        self.welcome_title.grid(row=0, column=0, sticky="w")

        self.profile_box = ctk.CTkFrame(self.header_frame, fg_color=p["entry"], corner_radius=8, border_width=1, border_color="#313244")
        self.profile_box.grid(row=0, column=1, sticky="e")

        self.profile_label = ctk.CTkLabel(
            self.profile_box,
            text="👤 Profilim",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=p["accent"]
        )
        self.profile_label.pack(padx=15, pady=8)

        self.display_card = ctk.CTkFrame(self.content_frame, fg_color=p["card"], corner_radius=12, border_width=1, border_color="#313244")
        self.display_card.grid(row=1, column=0, sticky="nsew")
        self.display_card.grid_rowconfigure(0, weight=1)
        self.display_card.grid_columnconfigure(0, weight=1)

        self.info_text = ctk.CTkLabel(
            self.display_card,
            text="Sol menüden bir seçenek seçerek içerikleri görüntüleyin.",
            font=ctk.CTkFont(size=14),
            text_color=p["text_sub"]
        )
        self.info_text.grid(row=0, column=0)

        self.settings_container = None
        self.color_menu = None

    def set_username(self, username):
        self.welcome_title.configure(text=f"Hoş Geldin, {username} 👋")

    def create_sidebar_button(self, text, row_idx, command):
        p = self.app.current_palette
        btn = ctk.CTkButton(
            self.sidebar_frame,
            text=text,
            fg_color="transparent",
            hover_color=p["entry"],
            text_color=p["text_main"],
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            corner_radius=8,
            command=command
        )
        btn.grid(row=row_idx, column=0, padx=15, pady=4, sticky="ew")
        self.sidebar_buttons.append(btn)
        return btn

    def clear_display(self):
        self.settings_container = None
        for widget in self.display_card.winfo_children():
            widget.destroy()

    def open_notes(self):
        self.clear_display()
        p = self.app.current_palette
        lbl = ctk.CTkLabel(self.display_card, text="📚 Ders Notları Alanı\nPaylaşılan notları buradan inceleyebilirsin.", font=ctk.CTkFont(size=15), text_color=p["text_main"])
        lbl.grid(row=0, column=0)

    def open_polls(self):
        self.clear_display()
        p = self.app.current_palette
        lbl = ctk.CTkLabel(self.display_card, text="📊 Kampüs Anketleri\nAktif oylamalara buradan katılabilirsin.", font=ctk.CTkFont(size=15), text_color=p["text_main"])
        lbl.grid(row=0, column=0)

    def open_events(self):
        self.clear_display()
        p = self.app.current_palette
        lbl = ctk.CTkLabel(self.display_card, text="🎉 Kampüs Etkinlikleri\nÜniversitedeki sosyal etkinlikleri takip et.", font=ctk.CTkFont(size=15), text_color=p["text_main"])
        lbl.grid(row=0, column=0)

    def open_settings(self):
        self.clear_display()
        p = self.app.current_palette

        self.settings_container = ctk.CTkFrame(self.display_card, fg_color="transparent")
        self.settings_container.grid(row=0, column=0, padx=40, pady=40, sticky="nw")

        title = ctk.CTkLabel(
            self.settings_container,
            text="⚙️ Hesap ve Uygulama Ayarları",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=p["text_main"]
        )
        title.grid(row=0, column=0, sticky="w", pady=(0, 20))

        color_label = ctk.CTkLabel(self.settings_container, text="Uygulama Tema ve Renk Seçenekleri", font=ctk.CTkFont(size=13, weight="bold"), text_color=p["text_sub"])
        color_label.grid(row=1, column=0, sticky="w", pady=(0, 8))

        self.color_menu = ctk.CTkSegmentedButton(
            self.settings_container,
            values=list(self.app.themes.keys()),
            command=self.on_theme_select,
            selected_color=p["accent"],
            selected_hover_color=p["hover"],
            unselected_color=p["entry"],
            text_color=p["text_main"]
        )
        self.color_menu.grid(row=2, column=0, sticky="w", pady=(0, 10))
        self.color_menu.set(self.app.current_theme_name)

    def on_theme_select(self, theme_name):
        self.app.update_global_theme(theme_name)

    def apply_theme(self):
        """Tema değiştiğinde arkaplanlar, kartlar, tüm metinler güncellenir ve ayarlar açıksa güvenle yenilenir"""
        p = self.app.current_palette

        self.configure(fg_color=p["bg"])
        self.sidebar_frame.configure(fg_color=p["sidebar"])
        self.logo_label.configure(text_color=p["text_main"])
        self.display_card.configure(fg_color=p["card"])
        self.profile_box.configure(fg_color=p["entry"])
        self.profile_label.configure(text_color=p["accent"])
        self.welcome_title.configure(text_color=p["text_main"])

        if hasattr(self, "info_text") and self.info_text.winfo_exists():
            self.info_text.configure(text_color=p["text_sub"])

        for btn in self.sidebar_buttons:
            btn.configure(text_color=p["text_main"], hover_color=p["entry"])

        if hasattr(self, "settings_container") and self.settings_container is not None:
            try:
                if self.settings_container.winfo_exists():
                    children = self.display_card.winfo_children()
                    if children and children[0] == self.settings_container:
                        self.open_settings()
            except Exception:
                pass
