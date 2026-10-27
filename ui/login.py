import customtkinter as ctk
from networking import server_interaction

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_register, on_login_success, app_controller=None):
        super().__init__(parent)
        self.switch_to_register = switch_to_register
        self.on_login_success = on_login_success
        self.app = app_controller

        p = self.app.current_palette if self.app else {
            "bg": "#11111B", "card": "#1E1E2E", "entry": "#181825",
            "accent": "#89B4FA", "hover": "#B4BEFE", "text_main": "#CDD6F4", "text_sub": "#A6ADC8"
        }

        self.configure(fg_color=p["bg"])
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Ana Giriş Kartı
        self.card_frame = ctk.CTkFrame(self, width=380, height=450, fg_color=p["card"], corner_radius=16, border_width=1, border_color="#313244")
        self.card_frame.grid(row=0, column=0)
        self.card_frame.grid_propagate(False)

        # Başlık
        self.title_label = ctk.CTkLabel(
            self.card_frame,
            text="Giriş Yap",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=p["text_main"]
        )
        self.title_label.pack(pady=(35, 20))

        # Kullanıcı Adı Girişi
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

        # Şifre ve Göz Butonu için Container Frame
        self.password_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.password_container.pack(pady=10)

        # Şifre Girişi
        self.password_entry = ctk.CTkEntry(
            self.password_container,
            placeholder_text="Şifre",
            show="*",
            width=230,
            height=40,
            fg_color=p["entry"],
            border_color="#313244",
            text_color=p["text_main"]
        )
        self.password_entry.pack(side="left", padx=(0, 5))

        # Şifreyi Göster/Gizle Butonu (Göz Sembolü)
        self.eye_btn = ctk.CTkButton(
            self.password_container,
            text="👁️",
            width=45,
            height=40,
            fg_color=p["entry"],
            hover_color=p["hover"],
            text_color=p["text_main"],
            command=self.toggle_password_visibility
        )
        self.eye_btn.pack(side="left")

        # Bilgi / Hata Mesajı
        self.info_label = ctk.CTkLabel(
            self.card_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=p["text_sub"]
        )
        self.info_label.pack(pady=5)

        # Giriş Yap Butonu
        self.login_btn = ctk.CTkButton(
            self.card_frame,
            text="Giriş Yap",
            width=280,
            height=40,
            fg_color=p["accent"],
            hover_color=p["hover"],
            text_color="#11111B",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.login_event
        )
        self.login_btn.pack(pady=15)

        # Kayıt Ol'a Geçiş Butonu
        self.switch_btn = ctk.CTkButton(
            self.card_frame,
            text="Hesabın yok mu? Kayıt Ol",
            fg_color="transparent",
            hover_color=p["entry"],
            text_color=p["text_sub"],
            font=ctk.CTkFont(size=12),
            command=self.switch_to_register
        )
        self.switch_btn.pack(pady=(0, 20))

    def toggle_password_visibility(self):
        """Şifrenin görünürlüğünü açar/kapatır ve ikonunu günceller"""
        if self.password_entry.cget("show") == "*":
            self.password_entry.configure(show="")
            self.eye_btn.configure(text="🔒")
        else:
            self.password_entry.configure(show="*")
            self.eye_btn.configure(text="👁️")

    def login_event(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.info_label.configure(text_color="#F38BA8", text="⚠️ Lütfen tüm alanları doldurun!")
            return

        try:
            response = server_interaction.send_login(username, password)

            if response.startswith("SUCCESS"):
                success_msg = response.split(":", 1)[1] if ":" in response else "Giriş başarılı!"
                self.info_label.configure(text_color="#A6E3A1", text=f"✅ {success_msg}")
                self.after(800, lambda: self.on_login_success(username))
            else:
                error_msg = response.split(":", 1)[1] if ":" in response else "Giriş başarısız"
                self.info_label.configure(text_color="#F38BA8", text=f"❌ {error_msg}")

        except Exception as e:
            self.info_label.configure(text_color="#F38BA8", text="❌ Sunucuya bağlanılamadı!")
            print(f"[NETWORK ERROR] {e}")

    def apply_theme(self):
        """Tema değiştiğinde giriş ekranı bileşenlerini gecikmesiz günceller"""
        if not self.app:
            return
        p = self.app.current_palette

        self.configure(fg_color=p["bg"])
        self.card_frame.configure(fg_color=p["card"])
        self.title_label.configure(text_color=p["text_main"])
        self.username_entry.configure(fg_color=p["entry"], text_color=p["text_main"])
        self.password_entry.configure(fg_color=p["entry"], text_color=p["text_main"])
        self.eye_btn.configure(fg_color=p["entry"], hover_color=p["hover"], text_color=p["text_main"])
        self.login_btn.configure(fg_color=p["accent"], hover_color=p["hover"])
        self.switch_btn.configure(hover_color=p["entry"], text_color=p["text_sub"])

        self.update_idletasks()
