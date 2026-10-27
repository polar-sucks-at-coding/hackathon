import customtkinter as ctk
from PIL import Image
import os
from login import LoginPage
from register import RegisterPage

ctk.deactivate_automatic_dpi_awareness()
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SAÜ Connect")
        self.geometry("900x580")
        self.minsize(800, 520)
        self.resizable(True, True)

        # Ana Izgara Yapısı (Sol Sabit Panel, Sağ Değişen Panel)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)  # Sol Marka Paneli
        self.grid_columnconfigure(1, weight=1)  # Sağ Form Alanı

        # ==========================================
        # 1. SOL PANEL: SABİT MARKA & LOGO
        # ==========================================
        self.brand_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1E1E2E")
        self.brand_frame.grid(row=0, column=0, sticky="nsew")

        self.brand_frame.grid_rowconfigure((0, 4), weight=1)
        self.brand_frame.grid_columnconfigure(0, weight=1)

        self.logo_path = "logo.jpeg"
        if os.path.exists(self.logo_path):
            img = Image.open(self.logo_path)
            self.logo_image = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 120))
            self.logo_label = ctk.CTkLabel(self.brand_frame, image=self.logo_image, text="")
            self.logo_label.grid(row=1, column=0, pady=(0, 15))
        else:
            self.logo_label = ctk.CTkLabel(self.brand_frame, text="🎓", font=ctk.CTkFont(size=64))
            self.logo_label.grid(row=1, column=0, pady=(0, 15))

        self.brand_title = ctk.CTkLabel(self.brand_frame, text="SAÜ Connect", font=ctk.CTkFont(size=30, weight="bold"), text_color="#FFFFFF")
        self.brand_title.grid(row=2, column=0, pady=(0, 5))

        self.brand_subtitle = ctk.CTkLabel(self.brand_frame, text="Sakarya Üniversitesi Öğrenci &\n Kampüs Etkileşim Platformu", font=ctk.CTkFont(size=13), text_color="#A6ADC8", justify="center")
        self.brand_subtitle.grid(row=3, column=0, pady=(0, 10))

        # ==========================================
        # 2. SAĞ PANEL: ÖN BELLEKLENMİŞ SAYFA YÖNETİCİSİ
        # ==========================================
        self.container = ctk.CTkFrame(self, corner_radius=0, fg_color="#11111B")
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Sayfaları hafızada önceden oluşturup cache'liyoruz (Sıfır gecikme / Smooth geçiş için)
        self.login_page = LoginPage(self.container, switch_to_register=self.show_register, on_login_success=self.on_login_success)
        self.register_page = RegisterPage(self.container, switch_to_login=self.show_login)

        # İki sayfayı da aynı grid hücresine üst üste yerleştiriyoruz
        self.login_page.grid(row=0, column=0, sticky="nsew")
        self.register_page.grid(row=0, column=0, sticky="nsew")

        # İlk açılışta login sayfasını öne getir
        self.show_login()

    def show_login(self):
        # Sayfayı yeniden oluşturmak yerine anında öne taşıyoruz (Sıfır siyah ekran)
        self.login_page.tkraise()

    def show_register(self):
        self.register_page.tkraise()

    def on_login_success(self):
        print("[BAŞARILI] Ana sayfaya yönlendiriliyor...")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
