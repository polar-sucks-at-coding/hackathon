import customtkinter as ctk
from networking import server_interaction

class RegisterPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_login, app_controller=None):
        super().__init__(parent)
        self.switch_to_login = switch_to_login
        self.app = app_controller

        p = self.app.current_palette if self.app else {
            "bg": "#11111B", "card": "#1E1E2E", "entry": "#181825",
            "accent": "#89B4FA", "hover": "#B4BEFE", "text_main": "#CDD6F4", "text_sub": "#A6ADC8"
        }

        self.configure(fg_color=p["bg"])
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Kayıt Kartı (Yeni alan için yükseklik 540 yapıldı)
        self.card_frame = ctk.CTkFrame(self, width=380, height=540, fg_color=p["card"], corner_radius=16, border_width=1, border_color="#313244")
        self.card_frame.grid(row=0, column=0)
        self.card_frame.grid_propagate(False)

        self.title_label = ctk.CTkLabel(
            self.card_frame,
            text="Kayıt Ol",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=p["text_main"]
        )
        self.title_label.pack(pady=(30, 15))

        self.username_entry = ctk.CTkEntry(
            self.card_frame,
            placeholder_text="Kullanıcı Adı",
            width=280,
            height=40,
            fg_color=p["entry"],
            border_color="#313244",
            text_color=p["text_main"]
        )
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(
            self.card_frame,
            placeholder_text="Şifre",
            show="*",
            width=280,
            height=40,
            fg_color=p["entry"],
            border_color="#313244",
            text_color=p["text_main"]
        )
        self.password_entry.pack(pady=10)

        # Şifre Doğrulama Alanı
        self.confirm_password_entry = ctk.CTkEntry(
            self.card_frame,
            placeholder_text="Şifreyi Tekrar Girin",
            show="*",
            width=280,
            height=40,
            fg_color=p["entry"],
            border_color="#313244",
            text_color=p["text_main"]
        )
        self.confirm_password_entry.pack(pady=10)

        self.info_label = ctk.CTkLabel(
            self.card_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=p["text_sub"]
        )
        self.info_label.pack(pady=5)

        self.register_btn = ctk.CTkButton(
            self.card_frame,
            text="Kayıt Ol",
            width=280,
            height=40,
            fg_color=p["accent"],
            hover_color=p["hover"],
            text_color="#11111B",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.register_event
        )
        self.register_btn.pack(pady=15)

        self.switch_btn = ctk.CTkButton(
            self.card_frame,
            text="Zaten hesabın var mı? Giriş Yap",
            fg_color="transparent",
            hover_color=p["entry"],
            text_color=p["text_sub"],
            font=ctk.CTkFont(size=12),
            command=self.switch_to_login
        )
        self.switch_btn.pack(pady=(0, 20))

    def register_event(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        if not username or not password or not confirm_password:
            self.info_label.configure(text_color="#F38BA8", text="⚠️ Lütfen tüm alanları doldurun!")
            return

        if password != confirm_password:
            self.info_label.configure(text_color="#F38BA8", text="⚠️ Şifreler eşleşmiyor!")
            return

        try:
            response = server_interaction.send_register(username, password)

            if response.startswith("SUCCESS"):
                success_msg = response.split(":", 1)[1] if ":" in response else "Kayıt başarılı!"
                self.info_label.configure(text_color="#A6E3A1", text=f"✅ {success_msg}")
                self.after(1000, self.switch_to_login)
            else:
                error_msg = response.split(":", 1)[1] if ":" in response else "Kayıt başarısız"
                self.info_label.configure(text_color="#F38BA8", text=f"❌ {error_msg}")

        except Exception as e:
            self.info_label.configure(text_color="#F38BA8", text="❌ Sunucuya bağlanılamadı!")
            print(f"[NETWORK ERROR] {e}")

    def apply_theme(self):
        """Tema değiştiğinde kayıt ekranı bileşenlerini gecikmesiz günceller"""
        if not self.app:
            return
        p = self.app.current_palette

        self.configure(fg_color=p["bg"])
        self.card_frame.configure(fg_color=p["card"])
        self.title_label.configure(text_color=p["text_main"])
        self.username_entry.configure(fg_color=p["entry"], text_color=p["text_main"])
        self.password_entry.configure(fg_color=p["entry"], text_color=p["text_main"])
        self.confirm_password_entry.configure(fg_color=p["entry"], text_color=p["text_main"])
        self.register_btn.configure(fg_color=p["accent"], hover_color=p["hover"])
        self.switch_btn.configure(hover_color=p["entry"], text_color=p["text_sub"])

        self.update_idletasks()
