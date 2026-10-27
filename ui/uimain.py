import sys
import os

# Projenin ana dizinini (hackathon/) Python path'ine ekle ki 'networking' ve diğer modüller bulunabilsin
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import customtkinter as ctk
from PIL import Image
from login import LoginPage
from register import RegisterPage
from mainmenu import MainMenuPage

# ... (geri kalan kodlar aynı kalır)

ctk.deactivate_automatic_dpi_awareness()
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SAÜ Connect")
        self.geometry("950x600")
        self.minsize(850, 540)
        self.resizable(True, True)

        # Temalar ve Renk Paletleri
        self.themes = {
            "Siyah (OLED)": {
                "bg": "#000000", "sidebar": "#0A0A0A", "card": "#121212",
                "entry": "#1A1A1A", "accent": "#FFFFFF", "hover": "#333333",
                "text_main": "#FFFFFF", "text_sub": "#A0A0A0"
            },
            "Beyaz (Clean)": {
                "bg": "#F5F5F7", "sidebar": "#FFFFFF", "card": "#FFFFFF",
                "entry": "#E5E5EA", "accent": "#007AFF", "hover": "#D1D1D6",
                "text_main": "#1D1D1F", "text_sub": "#86868B"
            },
            "Mavi (Modern)": {
                "bg": "#11111B", "sidebar": "#1E1E2E", "card": "#1E1E2E",
                "entry": "#181825", "accent": "#89B4FA", "hover": "#313244",
                "text_main": "#CDD6F4", "text_sub": "#A6ADC8"
            },
            "Krem / Bej": {
                "bg": "#1C1B18", "sidebar": "#262420", "card": "#262420",
                "entry": "#1E1C18", "accent": "#F5E0DC", "hover": "#383530",
                "text_main": "#E6E1DE", "text_sub": "#B8B3B0"
            },
            "Zümrüt Yeşili": {
                "bg": "#111813", "sidebar": "#18241D", "card": "#18241D",
                "entry": "#131C17", "accent": "#A6E3A1", "hover": "#223529",
                "text_main": "#D4E7D6", "text_sub": "#9FB3A2"
            }
        }

        self.current_theme_name = "Mavi (Modern)"
        self.current_palette = self.themes[self.current_theme_name]

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self, corner_radius=0, fg_color=self.current_palette["bg"])
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Sayfaları oluştururken app_controller=self veriyoruz
        self.login_page = LoginPage(self.container, switch_to_register=self.show_register, on_login_success=self.show_main_menu, app_controller=self)
        self.register_page = RegisterPage(self.container, switch_to_login=self.show_login, app_controller=self)
        self.main_menu_page = MainMenuPage(self.container, switch_to_login=self.show_login, app_controller=self)

        self.login_page.grid(row=0, column=0, sticky="nsew")
        self.register_page.grid(row=0, column=0, sticky="nsew")
        self.main_menu_page.grid(row=0, column=0, sticky="nsew")

        self.show_login()

    def update_global_theme(self, theme_name):
        """Seçilen temayı ana pencere, ana container ve TÜM sayfalara anında eşzamanlı uygular"""
        if theme_name in self.themes:
            self.current_theme_name = theme_name
            self.current_palette = self.themes[theme_name]

            if theme_name == "Beyaz (Clean)":
                ctk.set_appearance_mode("Light")
            else:
                ctk.set_appearance_mode("Dark")

            # 1. Ana pencere ve container renklerini anında sabitle
            self.configure(fg_color=self.current_palette["bg"])
            self.container.configure(fg_color=self.current_palette["bg"])

            # 2. Hangi sayfada olursa olsun TÜM sayfaların temasını eşzamanlı güncelle
            self.login_page.apply_theme()
            self.register_page.apply_theme()
            self.main_menu_page.apply_theme()

            print(f"[GLOBAL TEMA] Eşzamanlı güncellendi: {theme_name}")

    def show_login(self):
        self.login_page.tkraise()

    def show_register(self):
        self.register_page.tkraise()

    def show_main_menu(self, username):
        self.main_menu_page.set_username(username)
        self.main_menu_page.tkraise()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
