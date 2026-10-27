import customtkinter as ctk
import os
import sys

# 1. Projenin ana kök dizinini (/home/comp/Project/hackathon) Python yoluna ekle
current_dir = os.path.dirname(os.path.abspath(__file__))  # /home/comp/Project/hackathon/ui
parent_dir = os.path.dirname(current_dir)                 # /home/comp/Project/hackathon
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 2. Artık alt klasörler (ui ve networking) sorunsuz içe aktarılabilir
from ui.login import LoginPage
from ui.register import RegisterPage
from ui.mainmenu import MainMenuPage

# Tema Paletleri (Catppuccin Mocha ve alternatif modern temalar)
THEMES = {
    "Catppuccin Mocha": {
        "bg": "#11111B",
        "card": "#1E1E2E",
        "sidebar": "#181825",
        "entry": "#181825",
        "accent": "#89B4FA",
        "hover": "#B4BEFE",
        "text_main": "#CDD6F4",
        "text_sub": "#A6ADC8"
    },
    "Dracula Dark": {
        "bg": "#21222C",
        "card": "#282A36",
        "sidebar": "#191A21",
        "entry": "#44475A",
        "accent": "#BD93F9",
        "hover": "#FF79C6",
        "text_main": "#F8F8F2",
        "text_sub": "#6272A4"
    },
    "Emerald Night": {
        "bg": "#0F172A",
        "card": "#1E293B",
        "sidebar": "#090D16",
        "entry": "#334155",
        "accent": "#34D399",
        "hover": "#6EE7B7",
        "text_main": "#F1F5F9",
        "text_sub": "#94A3B8"
    },
    "Sunset Orange": {
        "bg": "#18181B",
        "card": "#27272A",
        "sidebar": "#09090B",
        "entry": "#3F3F46",
        "accent": "#FB923C",
        "hover": "#FDBA74",
        "text_main": "#FAFAFA",
        "text_sub": "#A1A1AA"
    },
    "Cyberpunk Neon": {
        "bg": "#05050A",
        "card": "#12121F",
        "sidebar": "#0A0A12",
        "entry": "#1E1E30",
        "accent": "#F43F5E",
        "hover": "#FB7185",
        "text_main": "#FFF1F2",
        "text_sub": "#FDA4AF"
    }
}

class SAUConnectApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Temel Ayarları
        self.title("SAÜ Connect - Kampüs Platformu")
        self.geometry("900x600")
        self.minsize(850, 550)

        # Tema Yönetimi Değişkenleri
        self.current_theme_name = "Catppuccin Mocha"
        self.themes = THEMES
        self.current_palette = self.themes[self.current_theme_name]

        # Ana pencere arkaplan rengini ayarla
        self.configure(fg_color=self.current_palette["bg"])

        # Grid Yapılandırması (Tüm sayfaların üst üste bindiği ortak alan)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Sayfaları Hafızada Tek Seferde Oluştur (Geçişlerde sıfır gecikme & titreme yok)
        self.login_page = LoginPage(
            parent=self,
            switch_to_register=self.show_register_page,
            on_login_success=self.show_main_menu,
            app_controller=self
        )
        self.register_page = RegisterPage(
            parent=self,
            switch_to_login=self.show_login_page,
            app_controller=self
        )
        self.main_menu_page = MainMenuPage(
            parent=self,
            switch_to_login=self.show_login_page,
            app_controller=self
        )

        # Tüm sayfaları aynı hücreye yerleştir (Üst üste bindirme)
        for page in (self.login_page, self.register_page, self.main_menu_page):
            page.grid(row=0, column=0, sticky="nsew")

        # Uygulama açılışında Giriş Sayfasını öne getir
        self.show_login_page()

    def show_login_page(self):
        """Giriş ekranını anında öne getirir"""
        self.login_page.tkraise()
        self.update_idletasks()

    def show_register_page(self):
        """Kayıt ekranını anında öne getirir"""
        self.register_page.tkraise()
        self.update_idletasks()

    def show_main_menu(self, username):
        """Ana menüyü öne getirir ve kullanıcı adını eşitler"""
        self.main_menu_page.set_username(username)

        # Güvenli kontrol: Notlar sekmesi henüz açılmadıysa hata vermesini önle
        if hasattr(self.main_menu_page, "notes_scroll_frame") and self.main_menu_page.notes_scroll_frame is not None:
            try:
                if self.main_menu_page.notes_scroll_frame.winfo_exists():
                    self.main_menu_page.load_notes_from_server()
            except Exception:
                pass

        self.main_menu_page.tkraise()
        self.update_idletasks()

    def update_global_theme(self, theme_name):
        """Global tema değiştirildiğinde aktif tüm sayfaların renklerini anında günceller"""
        if theme_name in self.themes:
            self.current_theme_name = theme_name
            self.current_palette = self.themes[theme_name]

            self.configure(fg_color=self.current_palette["bg"])

            # Hafızadaki tüm sayfalara tema güncelleme sinyali gönder
            for page in (self.login_page, self.register_page, self.main_menu_page):
                if hasattr(page, "apply_theme"):
                    page.apply_theme()

            self.update_idletasks()

if __name__ == "__main__":
    # CustomTkinter genel görünüm tercihleri
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    app = SAUConnectApp()
    app.mainloop()
