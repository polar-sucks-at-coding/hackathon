import customtkinter as ctk

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_register, on_login_success):
        super().__init__(parent, fg_color="transparent")
        self.switch_to_register = switch_to_register
        self.on_login_success = on_login_success

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Form Kartı
        self.card = ctk.CTkFrame(self, fg_color="transparent", width=380, height=500)
        self.card.grid(row=0, column=0)
        self.card.grid_propagate(False)
        self.card.grid_columnconfigure(0, weight=1)

        # Başlık
        self.welcome_label = ctk.CTkLabel(
            self.card,
            text="Hesabınıza Giriş Yapın",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#CDD6F4",
            anchor="w"
        )
        self.welcome_label.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # --- E-posta Alanı ---
        self.email_label = ctk.CTkLabel(self.card, text="E-posta Adresi", font=ctk.CTkFont(size=12, weight="bold"), text_color="#A6ADC8", anchor="w")
        self.email_label.grid(row=1, column=0, sticky="w", pady=(0, 4))
        self.username_entry = ctk.CTkEntry(self.card, height=42, placeholder_text="ogrenci@sakarya.edu.tr", border_color="#313244", fg_color="#181825", corner_radius=8)
        self.username_entry.grid(row=2, column=0, sticky="ew", pady=(0, 15))

        # --- Şifre Alanı ---
        self.pass_label = ctk.CTkLabel(self.card, text="Şifre", font=ctk.CTkFont(size=12, weight="bold"), text_color="#A6ADC8", anchor="w")
        self.pass_label.grid(row=3, column=0, sticky="w", pady=(0, 4))

        self.password_container = ctk.CTkFrame(self.card, fg_color="transparent")
        self.password_container.grid(row=4, column=0, sticky="ew", pady=(0, 2))
        self.password_container.grid_columnconfigure(0, weight=1)

        self.password_entry = ctk.CTkEntry(self.password_container, height=42, placeholder_text="••••••••", show="*", border_color="#313244", fg_color="#181825", corner_radius=8)
        self.password_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        # Göz Sembolü Butonu
        self.show_password_btn = ctk.CTkButton(
            self.password_container,
            text="👁",
            width=42,
            height=42,
            corner_radius=8,
            fg_color="#181825",
            hover_color="#313244",
            border_color="#313244",
            border_width=1,
            font=ctk.CTkFont(size=15),
            command=self.toggle_password_visibility
        )
        self.show_password_btn.grid(row=0, column=1, sticky="e")

        # Hata / Bilgi Mesajı Alanı
        self.info_label = ctk.CTkLabel(self.card, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color="#F38BA8", anchor="w", height=20)
        self.info_label.grid(row=5, column=0, sticky="w", pady=(0, 5))

        # --- Beni Hatırla & Şifremi Unuttum ---
        self.options_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.options_frame.grid(row=6, column=0, sticky="ew", pady=(5, 15))
        self.options_frame.grid_columnconfigure(0, weight=1)
        self.options_frame.grid_columnconfigure(1, weight=1)

        self.remember_checkbox = ctk.CTkCheckBox(self.options_frame, text="Beni Hatırla", font=ctk.CTkFont(size=12), text_color="#A6ADC8", checkbox_width=18, checkbox_height=18, corner_radius=4)
        self.remember_checkbox.grid(row=0, column=0, sticky="w")

        self.forgot_btn = ctk.CTkButton(self.options_frame, text="Şifremi Unuttum?", fg_color="transparent", text_color="#89B4FA", hover=False, font=ctk.CTkFont(size=12), width=0, command=self.forgot_password_event)
        self.forgot_btn.grid(row=0, column=1, sticky="e")

        # --- Giriş Yap Butonu ---
        self.login_button = ctk.CTkButton(self.card, text="Giriş Yap", height=42, corner_radius=8, fg_color="#89B4FA", hover_color="#B4BEFE", text_color="#11111B", font=ctk.CTkFont(size=14, weight="bold"), command=self.login_event)
        self.login_button.grid(row=7, column=0, sticky="ew", pady=(0, 15))

        # --- Kayıt Ol Yönlendirme ---
        self.signup_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.signup_frame.grid(row=8, column=0, sticky="ew")
        self.signup_frame.grid_columnconfigure(0, weight=1)

        self.signup_inner = ctk.CTkFrame(self.signup_frame, fg_color="transparent")
        self.signup_inner.grid(row=0, column=0, sticky="")

        self.signup_label = ctk.CTkLabel(self.signup_inner, text="Hesabınız yok mu?", font=ctk.CTkFont(size=12), text_color="#A6ADC8")
        self.signup_label.pack(side="left", padx=(0, 4))

        self.signup_btn = ctk.CTkButton(self.signup_inner, text="Kayıt Ol", fg_color="transparent", text_color="#89B4FA", hover=False, font=ctk.CTkFont(size=12, weight="bold"), width=0, command=self.switch_to_register)
        self.signup_btn.pack(side="left")

    def toggle_password_visibility(self):
        if self.password_entry.cget("show") == "*":
            self.password_entry.configure(show="")
            self.show_password_btn.configure(text="🔒")
        else:
            self.password_entry.configure(show="*")
            self.show_password_btn.configure(text="👁")

    def forgot_password_event(self):
        self.info_label.configure(text_color="#F38BA8", text="⚠️ Şifre sıfırlama bağlantısı gönderildi! (demo)")

    def login_event(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            self.info_label.configure(text_color="#F38BA8", text="⚠️ Lütfen tüm alanları doldurun!")
            return
        self.info_label.configure(text="")
        print(f"[GİRİŞ] {username}")
        self.on_login_success()
