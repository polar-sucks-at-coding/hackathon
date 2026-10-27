import customtkinter as ctk
from networking import server_interaction

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
        self.btn_notes = self.create_sidebar_button("📖  Ders Notları", 1, self.open_notes)
        self.btn_polls = self.create_sidebar_button("📊  Anketler", 2, self.open_polls)
        self.btn_events = self.create_sidebar_button("❖  Takımlar", 3, self.open_events)
        self.btn_settings = self.create_sidebar_button("⚙️  Ayarlar", 4, self.open_settings)

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
            text="◆ Profilim",
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
        self.add_note_btn = None
        self.note_title_entry = None
        self.note_content_text = None
        self.modal_info_lbl = None

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
        self.add_note_btn = None
        for widget in self.display_card.winfo_children():
            widget.destroy()

    def open_notes(self):
        self.clear_display()
        p = self.app.current_palette

        self.display_card.grid_rowconfigure(0, weight=0)
        self.display_card.grid_rowconfigure(1, weight=1)
        self.display_card.grid_columnconfigure(0, weight=1)

        notes_header_frame = ctk.CTkFrame(self.display_card, fg_color="transparent")
        notes_header_frame.grid(row=0, column=0, padx=30, pady=25, sticky="ew")
        notes_header_frame.grid_columnconfigure(0, weight=1)
        notes_header_frame.grid_columnconfigure(1, weight=0)

        text_container = ctk.CTkFrame(notes_header_frame, fg_color="transparent")
        text_container.grid(row=0, column=0, sticky="w")

        lbl_title = ctk.CTkLabel(
            text_container,
            text="📖 Ders Notları Alanı",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=p["text_main"]
        )
        lbl_title.pack(anchor="w", pady=(0, 2))

        lbl_sub = ctk.CTkLabel(
            text_container,
            text="Paylaşılan notları buradan inceleyebilirsin.",
            font=ctk.CTkFont(size=13),
            text_color=p["text_sub"]
        )
        lbl_sub.pack(anchor="w")

        self.add_note_btn = ctk.CTkButton(
            notes_header_frame,
            text="+ Not Ekle",
            width=110,
            height=36,
            fg_color=p["accent"],
            hover_color=p["hover"],
            text_color="#11111B",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8,
            command=self.open_add_note_modal
        )
        self.add_note_btn.grid(row=0, column=1, sticky="e")

        self.notes_scroll_frame = ctk.CTkScrollableFrame(self.display_card, fg_color=p["entry"], corner_radius=10, border_width=1, border_color="#313244")
        self.notes_scroll_frame.grid(row=1, column=0, padx=30, pady=(0, 30), sticky="nsew")
        self.notes_scroll_frame.grid_columnconfigure(0, weight=1)

        self.load_notes_from_server()

    def load_notes_from_server(self):
        p = self.app.current_palette
        for widget in self.notes_scroll_frame.winfo_children():
            widget.destroy()

        try:
            response = server_interaction.send_get_all_notes()

            if response.startswith("SUCCESS"):
                data = response.split(":", 1)[1]
                if data == "No notes found":
                    lbl = ctk.CTkLabel(self.notes_scroll_frame, text="Henüz ders notu yüklenmemiş. İlk notu sen ekle!", text_color=p["text_sub"], font=ctk.CTkFont(size=13))
                    lbl.pack(pady=40)
                    return

                note_items = data.split(";")
                for item in note_items:
                    if not item.strip():
                        continue

                    parts = item.split("|")
                    note_id = parts[0].split("=")[1]
                    note_title = parts[1].split("=")[1]
                    note_likes = parts[2].split("=")[1] if len(parts) > 2 else "0"
                    note_author = parts[3].split("=")[1] if len(parts) > 3 else "Bilinmiyor"

                    card = ctk.CTkFrame(self.notes_scroll_frame, fg_color=p["card"], corner_radius=8, border_width=1, border_color="#313244", height=60)
                    card.pack(fill="x", padx=10, pady=6)
                    card.pack_propagate(False)

                    title_btn = ctk.CTkButton(
                        card,
                        text=f"◆  {note_title}  •  Yazan: {note_author}  (❤️ {note_likes})",
                        fg_color="transparent",
                        hover_color=p["entry"],
                        text_color=p["text_main"],
                        anchor="w",
                        font=ctk.CTkFont(size=13, weight="bold"),
                        command=lambda nid=note_id: self.open_note_detail(nid)
                    )
                    title_btn.pack(fill="both", expand=True, padx=10)

            else:
                lbl = ctk.CTkLabel(self.notes_scroll_frame, text="Notlar yüklenirken hata oluştu.", text_color="#F38BA8", font=ctk.CTkFont(size=13))
                lbl.pack(pady=40)

        except Exception as e:
            print(f"[ERROR] {e}")
            lbl = ctk.CTkLabel(self.notes_scroll_frame, text="Sunucuya bağlanılamadı!", text_color="#F38BA8", font=ctk.CTkFont(size=13))
            lbl.pack(pady=40)

    def open_note_detail(self, note_id):
        p = self.app.current_palette
        response = server_interaction.send_get_note(note_id)

        detail_modal = ctk.CTkToplevel(self)
        detail_modal.title("Ders Notu Detayı")
        detail_modal.geometry("450x420")
        detail_modal.resizable(False, False)
        detail_modal.configure(fg_color=p["bg"])
        detail_modal.grab_set()

        if response.startswith("SUCCESS"):
            data_part = response.split(":", 1)[1]
            fields = data_part.split("|")
            title = fields[1].split("=")[1]
            content = fields[2].split("=")[1]
            likes = fields[3].split("=")[1]
            author = fields[4].split("=")[1] if len(fields) > 4 else "Bilinmiyor"

            lbl_title = ctk.CTkLabel(detail_modal, text=title, font=ctk.CTkFont(size=20, weight="bold"), text_color=p["accent"])
            lbl_title.pack(padx=30, pady=(20, 5), anchor="w")

            lbl_author = ctk.CTkLabel(detail_modal, text=f"◆ Paylaşan: {author}", font=ctk.CTkFont(size=12, weight="bold"), text_color=p["text_sub"])
            lbl_author.pack(padx=30, anchor="w", pady=(0, 10))

            txt_content = ctk.CTkTextbox(detail_modal, width=380, height=200, fg_color=p["entry"], text_color=p["text_main"], font=ctk.CTkFont(size=13))
            txt_content.pack(padx=30, pady=5)
            txt_content.insert("0.0", content)
            txt_content.configure(state="disabled")

            lbl_likes = ctk.CTkLabel(detail_modal, text=f"❤️ Beğeni Sayısı: {likes}", font=ctk.CTkFont(size=12), text_color=p["text_sub"])
            lbl_likes.pack(padx=30, anchor="w", pady=(10, 0))

        else:
            err_lbl = ctk.CTkLabel(detail_modal, text="Not detayları alınamadı!", text_color="#F38BA8", font=ctk.CTkFont(size=14))
            err_lbl.pack(padx=30, pady=50)

    def open_add_note_modal(self):
        p = self.app.current_palette

        modal = ctk.CTkToplevel(self)
        modal.title("Yeni Ders Notu Ekle")
        modal.geometry("400x460")
        modal.resizable(False, False)
        modal.configure(fg_color=p["bg"])
        modal.grab_set()

        title_lbl = ctk.CTkLabel(modal, text="📖 Yeni Not Paylaş", font=ctk.CTkFont(size=18, weight="bold"), text_color=p["text_main"])
        title_lbl.pack(pady=(25, 15))

        self.note_title_entry = ctk.CTkEntry(
            modal,
            placeholder_text="Not Başlığı (Örn: Matematik Vize)",
            width=320,
            height=40,
            fg_color=p["entry"],
            border_color="#313244",
            text_color=p["text_main"]
        )
        self.note_title_entry.pack(pady=10)

        self.note_content_text = ctk.CTkTextbox(
            modal,
            width=320,
            height=160,
            fg_color=p["entry"],
            border_color="#313244",
            text_color=p["text_sub"]
        )
        self.note_content_text.pack(pady=10)
        self.note_content_text.insert("0.0", "Not içeriğini buraya yazın...")

        self.note_content_text.bind("<FocusIn>", self.on_textbox_focus_in)
        self.note_content_text.bind("<FocusOut>", self.on_textbox_focus_out)

        self.modal_info_lbl = ctk.CTkLabel(modal, text="", font=ctk.CTkFont(size=12), text_color=p["text_sub"])
        self.modal_info_lbl.pack(pady=5)

        save_btn = ctk.CTkButton(
            modal,
            text="Notu Kaydet",
            width=320,
            height=40,
            fg_color=p["accent"],
            hover_color=p["hover"],
            text_color="#11111B",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self.save_note_to_server(modal)
        )
        save_btn.pack(pady=15)

    def on_textbox_focus_in(self, event):
        p = self.app.current_palette
        current_text = self.note_content_text.get("0.0", "end").strip()
        if current_text == "Not içeriğini buraya yazın...":
            self.note_content_text.delete("0.0", "end")
            self.note_content_text.configure(text_color=p["text_main"])

    def on_textbox_focus_out(self, event):
        p = self.app.current_palette
        current_text = self.note_content_text.get("0.0", "end").strip()
        if not current_text:
            self.note_content_text.insert("0.0", "Not içeriğini buraya yazın...")
            self.note_content_text.configure(text_color=p["text_sub"])

    def save_note_to_server(self, modal_window):
        title = self.note_title_entry.get().strip()
        content = self.note_content_text.get("0.0", "end").strip()
        author = getattr(self, "current_username", "Misafir")

        if not title or not content or content == "Not içeriğini buraya yazın...":
            self.modal_info_lbl.configure(text_color="#F38BA8", text="⚠️ Lütfen tüm alanları doldurun!")
            return

        try:
            response = server_interaction.send_create_note(title, content, author)

            if response.startswith("SUCCESS"):
                self.modal_info_lbl.configure(text_color="#A6E3A1", text="✅ Not başarıyla kaydedildi!")
                modal_window.after(800, modal_window.destroy)
                self.open_notes()
            else:
                error_msg = response.split(":", 1)[1] if ":" in response else "Kayıt başarısız"
                self.modal_info_lbl.configure(text_color="#F38BA8", text=f"❌ {error_msg}")

        except Exception as e:
            self.modal_info_lbl.configure(text_color="#F38BA8", text="❌ Sunucuya bağlanılamadı!")
            print(f"[NETWORK ERROR] {e}")

    def open_polls(self):
        self.clear_display()
        p = self.app.current_palette
        self.display_card.grid_rowconfigure(0, weight=1)
        self.display_card.grid_columnconfigure(0, weight=1)
        lbl = ctk.CTkLabel(self.display_card, text="📊 Kampüs Anketleri\nAktif oylamalara buradan katılabilirsin.", font=ctk.CTkFont(size=15), text_color=p["text_main"])
        lbl.grid(row=0, column=0)

    def open_events(self):
        self.clear_display()
        p = self.app.current_palette
        self.display_card.grid_rowconfigure(0, weight=1)
        self.display_card.grid_columnconfigure(0, weight=1)
        lbl = ctk.CTkLabel(self.display_card, text="❖ Takım Oluşturma-Katılma sistemi\nÜniversitedeki projelere katıl.", font=ctk.CTkFont(size=15), text_color=p["text_main"])
        lbl.grid(row=0, column=0)

    def open_settings(self):
        self.clear_display()
        p = self.app.current_palette
        self.display_card.grid_rowconfigure(0, weight=1)
        self.display_card.grid_columnconfigure(0, weight=1)

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

        if hasattr(self, "add_note_btn") and self.add_note_btn is not None and self.add_note_btn.winfo_exists():
            self.add_note_btn.configure(fg_color=p["accent"], hover_color=p["hover"])

        if hasattr(self, "settings_container") and self.settings_container is not None:
            try:
                if self.settings_container.winfo_exists():
                    children = self.display_card.winfo_children()
                    if children and children[0] == self.settings_container:
                        self.open_settings()
            except Exception:
                pass
