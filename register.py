import customtkinter as ctk
# Networking klasöründen interaction modülünü içeri aktarıyoruz
# (Eğer register.py ile server_interaction aynı klasördeyse doğrudan import edebilirsin)
from networking import server_interaction

class RegisterPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_login):
        super().__init__(parent, fg_color="transparent")
        self.switch_to_login = switch_to_login

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
            text="Yeni Hesap Oluştur",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#CDD6F4",
            anchor="w"
        )
        self.welcome_label.grid(row=0, column=0, sticky="w", pady=(0, 15))

        # --- Ad Soyad / Kullanıcı Adı Alanı ---
        self.name_label = ctk.CTkLabel(self.card, text="Kullanıcı Adı", font=ctk.CTkFont(size=12, weight="bold"), text_color="#A6ADC8", anchor="w")
        self.name_label.grid(row=1, column=0, sticky="w", pady=(0, 2))
        self.name_entry = ctk.CTkEntry(self.card, height=40, placeholder_text="Kullanıcı adınızı girin", border_color="#313244", fg_color="#181825", corner_radius=8)
        self.name_entry.grid(row=2, column=0, sticky="ew", pady=(0, 12))

        # --- Şifre Alanı ---
        self.pass_label = ctk.CTkLabel(self.card, text="Şifre", font=ctk.CTkFont(size=12, weight="bold"), text_color="#A6ADC8", anchor="w")
        self.pass_label.grid(row=3, column=0, sticky="w", pady=(0, 2))
        self.password_entry = ctk.CTkEntry(self.card, height=40, placeholder_text="••••••••", show="*", border_color="#313244", fg_color="#181825", corner_radius=8)
        self.password_entry.grid(row=4, column=0, sticky="ew", pady=(0, 12))

        # --- Şifre Tekrar Alanı ---
        self.pass_confirm_label = ctk.CTkLabel(self.card, text="Şifre (Tekrar)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#A6ADC8", anchor="w")
        self.pass_confirm_label.grid(row=5, column=0, sticky="w", pady=(0, 2))
        self.password_confirm_entry = ctk.CTkEntry(self.card, height=40, placeholder_text="••••••••", show="*", border_color="#313244", fg_color="#181825", corner_radius=8)
        self.password_confirm_entry.grid(row=6, column=0, sticky="ew", pady=(0, 2))

        # Hata Mesajı Alanı
        self.info_label = ctk.CTkLabel(self.card, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color="#F38BA8", anchor="w", height=18)
        self.info_label.grid(row=7, column=0, sticky="w", pady=(0, 5))

        # --- Kayıt Ol Butonu ---
        self.register_button = ctk.CTkButton(self.card, text="Kayıt Ol", height=42, corner_radius=8, fg_color="#89B4FA", hover_color="#B4BEFE", text_color="#11111B", font=ctk.CTkFont(size=14, weight="bold"), command=self.register_event)
        self.register_button.grid(row=8, column=0, sticky="ew", pady=(0, 15))

        # --- Giriş Sayfasına Dönüş ---
        self.login_redirect_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.login_redirect_frame.grid(row=9, column=0, sticky="ew")
        self.login_redirect_frame.grid_columnconfigure(0, weight=1)

        self.login_redirect_inner = ctk.CTkFrame(self.login_redirect_frame, fg_color="transparent")
        self.login_redirect_inner.grid(row=0, column=0, sticky="")

        self.login_label = ctk.CTkLabel(self.login_redirect_inner, text="Zaten hesabınız var mı?", font=ctk.CTkFont(size=12), text_color="#A6ADC8")
        self.login_label.pack(side="left", padx=(0, 4))

        self.login_btn = ctk.CTkButton(self.login_redirect_inner, text="Giriş Yap", fg_color="transparent", text_color="#89B4FA", hover=False, font=ctk.CTkFont(size=12, weight="bold"), width=0, command=self.switch_to_login)
        self.login_btn.pack(side="left")

    def register_event(self):
        username = self.name_entry.get().strip()
        password = self.password_entry.get().strip()
        password_confirm = self.password_confirm_entry.get().strip()

        # 1. Boş Alan Kontrolü
        if not username or not password or not password_confirm:
            self.info_label.configure(text_color="#F38BA8", text="⚠️ Lütfen tüm alanları eksiksiz doldurun!")
            return

        # 2. Şifre Eşleşme Kontrolü
        if password != password_confirm:
            self.info_label.configure(text_color="#F38BA8", text="❌ Şifreler birbiriyle uyuşmuyor!")
            return

        # 3. Sunucuya İstek Atma (Networking Entegrasyonu)
        try:
            # server_interaction.py içerisindeki fonksiyonu çağırıyoruz
            response = server_interaction.send_register(username, password)

            # Sunucudan gelen cevabı işliyoruz (Örn: "SUCCESS:Account created!" veya "ERROR:Username already exists")
            if response.startswith("SUCCESS"):
                self.info_label.configure(text_color="#A6E3A1", text="✅ Kayıt başarılı! Giriş sayfasına yönlendiriliyorsunuz...")
                # 1 saniye sonra smooth bir şekilde login ekranına geri at
                self.after(1000, self.switch_to_login)
            else:
                # Sunucudan gelen hata mesajı (Örn: "ERROR:Username already exists" -> "Username already exists")
                error_msg = response.split(":", 1)[1] if ":" in response else "Bilinmeyen hata"
                self.info_label.configure(text_color="#F38BA8", text=f"❌ {error_msg}")

        except Exception as e:
            self.info_label.configure(text_color="#F38BA8", text="❌ Sunucuya bağlanılamadı!")
            print(f"[NETWORK ERROR] {e}")
