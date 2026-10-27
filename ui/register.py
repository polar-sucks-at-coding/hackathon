import customtkinter as ctk
from PIL import Image
import os
from networking import server_interaction

class RegisterPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_login=None, app_controller=None, **kwargs):
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

        # Ana Kart (Boyut: 720x440 - Login ile birebir aynı)
        self.card_frame = ctk.CTkFrame(self, width=720, height=440, fg_color=p["card"], corner_radius=20, border_width=1, border_color="#313244")
        self.card_frame.grid(row=0, column=0)
        self.card_frame.grid_propagate(False)
        self.card_frame.grid_columnconfigure(0, weight=1)
        self.card_frame.grid_columnconfigure(1, weight=1)
        self.card_frame.grid_rowconfigure(0, weight=1)

        # ==========================================
        # SOL TARAF: Logo & Marka Alanı
        # ==========================================
        self.left_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.left_inner = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.left_inner.place(relx=0.5, rely=0.5, anchor="center")

        self.logo_image = None
        if os.path.exists("logo.jpeg"):
            try:
                pil_img = Image.open("logo.jpeg")
                self.logo_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(80, 80))
                self.logo_label = ctk.CTkLabel(self.left_inner, text="", image=self.logo_image)
                self.logo_label.pack(pady=(0, 15))
            except Exception as e:
                print(f"[LOGO ERROR] {e}")

        self.brand_title = ctk.CTkLabel(
            self.left_inner,
            text="🎓 SAÜ Connect",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=p["accent"]
        )
        self.brand_title.pack(pady=(0, 5))

        self.brand_desc = ctk.CTkLabel(
            self.left_inner,
            text="Kampüs İletişim ve Paylaşım Platformu",
            font=ctk.CTkFont(size=12),
            text_color=p["text_sub"],
            justify="center"
        )
        self.brand_desc.pack()

        # ==========================================
        # SAĞ TARAF: Kayıt Formu
        # ==========================================
        self.right_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.right_inner = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.right_inner.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = ctk.CTkLabel(
            self.right_inner,
            text="Hesap Oluştur",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=p["text_main"]
        )
        self.title_label.pack(anchor="w", pady=(0, 8))

        self.username_entry = ctk.CTkEntry(
            self.right_inner,
            placeholder_text="Kullanıcı Adı",
            width=270,
            height=36,
            fg_color=p["entry"],
            border_color="#313244",
            text_color=p["text_main"],
            corner_radius=8
        )
        self.username_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(
            self.right_inner,
            placeholder_text="Şifre",
            show="*",
            width=270,
            height=36,
            fg_color=p["entry"],
            border_color="#313244",
            text_color=p["text_main"],
            corner_radius=8
        )
        self.password_entry.pack(pady=5)

        self.confirm_password_entry = ctk.CTkEntry(
            self.right_inner,
            placeholder_text="Şifreyi Tekrar Girin",
            show="*",
            width=270,
            height=36,
            fg_color=p["entry"],
            border_color="#313244",
            text_color=p["text_main"],
            corner_radius=8
        )
        self.confirm_password_entry.pack(pady=5)

        self.info_label = ctk.CTkLabel(
            self.right_inner,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=p["text_sub"]
        )
        self.info_label.pack(pady=2)

        self.register_btn = ctk.CTkButton(
            self.right_inner,
            text="Kayıt Ol",
            width=270,
            height=38,
            fg_color=p["accent"],
            hover_color=p["hover"],
            text_color="#11111B",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8,
            command=self.register_event
        )
        self.register_btn.pack(pady=8)

        self.switch_btn = ctk.CTkButton(
            self.right_inner,
            text="Zaten hesabın var mı? Giriş Yap",
            fg_color="transparent",
            hover_color=p["entry"],
            text_color=p["text_sub"],
            font=ctk.CTkFont(size=12),
            command=self.open_login_page
        )
        self.switch_btn.pack()

    def reset_fields(self):
        """Kayıt alanlarını sıfırlar"""
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.confirm_password_entry.delete(0, "end")
        self.info_label.configure(text="")
        self.register_btn.configure(state="normal", text="Kayıt Ol")

    def open_login_page(self):
        self.reset_fields()
        if self.switch_to_login:
            self.switch_to_login()

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
            self.info_label.configure(text_color="#A6ADC8", text="⏳ Hesap oluşturuluyor...")
            self.register_btn.configure(state="disabled")
            self.update_idletasks()

            response = server_interaction.send_register(username, password)
            if isinstance(response, dict) and response.get("status") == "success":
                success_msg = response.get("message", "Kayıt başarılı!")
                self.info_label.configure(text_color="#A6E3A1", text=f"✅ {success_msg}")
                self.after(1000, self.open_login_page)
            else:
                error_msg = response.get("message", "Kayıt başarısız") if isinstance(response, dict) else "Kayıt başarısız"
                self.info_label.configure(text_color="#F38BA8", text=f"❌ {error_msg}")
                self.register_btn.configure(state="normal", text="Kayıt Ol")
        except Exception as e:
            self.info_label.configure(text_color="#F38BA8", text="❌ Sunucuya bağlanılamadı!")
            self.register_btn.configure(state="normal", text="Kayıt Ol")
            print(f"[NETWORK ERROR] {e}")

    def apply_theme(self):
        if not self.app:
            return
        p = self.app.current_palette
        self.configure(fg_color=p["bg"])
        self.card_frame.configure(fg_color=p["card"])
        self.brand_title.configure(text_color=p["accent"])
        self.brand_desc.configure(text_color=p["text_sub"])
        self.title_label.configure(text_color=p["text_main"])
        self.username_entry.configure(fg_color=p["entry"], text_color=p["text_main"])
        self.password_entry.configure(fg_color=p["entry"], text_color=p["text_main"])
        self.confirm_password_entry.configure(fg_color=p["entry"], text_color=p["text_main"])
        self.register_btn.configure(fg_color=p["accent"], hover_color=p["hover"])
        self.switch_btn.configure(hover_color=p["entry"], text_color=p["text_sub"])
        self.update_idletasks()
