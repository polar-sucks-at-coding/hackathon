import customtkinter as ctk
import os
import sys
import subprocess
import shutil
import base64
from tkinter import filedialog
from networking import server_interaction

def open_native_file_dialog(title="Dosya Seçin"):
    if sys.platform.startswith("linux") and shutil.which("zenity"):
        try:
            cmd = ["zenity", "--file-selection", f"--title={title}"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                path = result.stdout.strip()
                return path if path else None
            else:
                return None
        except Exception as e:
            print(f"[ZENITY ERROR] {e}")

    return filedialog.askopenfilename(title=title)

def save_native_file_dialog(initialfile="", title="Dosya Kaydet"):
    if sys.platform.startswith("linux") and shutil.which("zenity"):
        try:
            cmd = ["zenity", "--file-selection", "--save", f"--filename={initialfile}", f"--title={title}", "--confirm-overwrite"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                path = result.stdout.strip()
                return path if path else None
            else:
                return None
        except Exception as e:
            print(f"[ZENITY ERROR] {e}")

    return filedialog.asksaveasfilename(initialfile=initialfile, title=title)

class MainMenuPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_login, app_controller):
        super().__init__(parent, fg_color=app_controller.current_palette["bg"])
        self.switch_to_login = switch_to_login
        self.app = app_controller
        self.current_username = "Misafir"
        self.active_sub_tab = "notes"  # "notes" veya "requests"
        p = self.app.current_palette

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # ==========================================
        # 1. SOL MENÜ (SIDEBAR)
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=p["sidebar"])
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)
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
        self.btn_social = self.create_sidebar_button("👥  Sosyal", 4, self.open_social)
        self.btn_profile = self.create_sidebar_button("👤  Profilim", 5, self.open_profile)
        self.btn_settings = self.create_sidebar_button("⚙️  Ayarlar", 6, self.open_settings)

        self.logout_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="🚪 Çıkış Yap",
            fg_color="#F38BA8",
            hover_color="#EBA0AC",
            text_color="#11111B",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            corner_radius=8,
            command=self.handle_logout_action
        )
        self.logout_btn.grid(row=8, column=0, padx=20, pady=20, sticky="ew")

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

        self.profile_btn = ctk.CTkButton(
            self.header_frame,
            text="👤 Profilim",
            fg_color=p["entry"],
            hover_color=p["hover"],
            text_color=p["accent"],
            font=ctk.CTkFont(size=12, weight="bold"),
            height=34,
            corner_radius=8,
            border_width=1,
            border_color="#313244",
            command=self.open_profile
        )
        self.profile_btn.grid(row=0, column=1, sticky="e")

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
        self.action_btn = None
        self.search_entry = None
        self.sort_option = None
        self.sub_tab_segment = None

    def handle_logout_action(self):
        if self.current_username:
            server_interaction.send_logout(self.current_username)

        if hasattr(self.app, "login_page") and self.app.login_page:
            if hasattr(self.app.login_page, "reset_fields"):
                self.app.login_page.reset_fields()

        if hasattr(self.app, "register_page") and self.app.register_page:
            if hasattr(self.app.register_page, "reset_fields"):
                self.app.register_page.reset_fields()

        self.switch_to_login()

    def set_username(self, username):
        self.current_username = username
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
        self.action_btn = None
        self.search_entry = None
        self.sort_option = None
        self.sub_tab_segment = None
        for widget in self.display_card.winfo_children():
            widget.destroy()

    def open_notes(self):
        self.clear_display()
        p = self.app.current_palette

        self.display_card.grid_rowconfigure(0, weight=0)
        self.display_card.grid_rowconfigure(1, weight=1)
        self.display_card.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.display_card, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=30, pady=20, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=0)

        self.sub_tab_segment = ctk.CTkSegmentedButton(
            header_frame,
            values=["📖 Ders Notları", "🙋‍♂️ Not İstekleri"],
            command=self.on_sub_tab_change,
            selected_color=p["accent"],
            selected_hover_color=p["hover"],
            unselected_color=p["entry"],
            text_color=p["text_main"],
            height=36,
            corner_radius=8
        )
        self.sub_tab_segment.grid(row=0, column=0, sticky="w", padx=(0, 15))

        initial_tab_name = "📖 Ders Notları" if self.active_sub_tab == "notes" else "🙋‍♂️ Not İstekleri"
        self.sub_tab_segment.set(initial_tab_name)

        self.controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        self.controls_frame.grid(row=0, column=1, sticky="ew", padx=10)
        self.controls_frame.grid_columnconfigure(1, weight=1)

        self.sort_option = ctk.CTkOptionMenu(
            self.controls_frame,
            values=["❤️ Beğeniye Göre", "📅 Tarihe Göre (En Yeni)", "🔤 A'dan Z'ye", "🔤 Z'den A'ya"],
            command=self.on_sort_change,
            height=36,
            width=165,
            fg_color=p["entry"],
            button_color=p["accent"],
            button_hover_color=p["hover"],
            text_color=p["text_main"],
            dropdown_fg_color=p["card"],
            dropdown_hover_color=p["entry"],
            dropdown_text_color=p["text_main"],
            corner_radius=8
        )
        self.sort_option.grid(row=0, column=0, padx=(0, 10), sticky="w")
        self.sort_option.set("❤️ Beğeniye Göre")

        self.search_entry = ctk.CTkEntry(
            self.controls_frame,
            placeholder_text="🔍 Notlarda ara...",
            height=36,
            fg_color=p["entry"],
            border_color="#313244",
            text_color=p["text_main"],
            corner_radius=8
        )
        self.search_entry.grid(row=0, column=1, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        self.action_btn = ctk.CTkButton(
            header_frame,
            text="+ Not Ekle",
            width=120,
            height=36,
            fg_color=p["accent"],
            hover_color=p["hover"],
            text_color="#11111B",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8
        )
        self.action_btn.grid(row=0, column=2, sticky="e")

        self.scroll_frame = ctk.CTkScrollableFrame(self.display_card, fg_color=p["entry"], corner_radius=10, border_width=1, border_color="#313244")
        self.scroll_frame.grid(row=1, column=0, padx=30, pady=(0, 30), sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self.render_active_sub_tab()

    def on_sub_tab_change(self, value):
        if value == "📖 Ders Notları":
            self.active_sub_tab = "notes"
        else:
            self.active_sub_tab = "requests"
        self.render_active_sub_tab()

    def render_active_sub_tab(self):
        p = self.app.current_palette

        if self.active_sub_tab == "notes":
            self.action_btn.configure(text="+ Not Ekle", command=self.open_add_note_modal)
            self.sort_option.grid()
            self.search_entry.configure(placeholder_text="🔍 Notlarda ara...")
            self.load_notes_from_server()
        else:
            self.action_btn.configure(text="+ İstek Ekle", command=self.open_add_request_modal)
            self.sort_option.grid_remove()
            self.search_entry.configure(placeholder_text="🔍 İsteklerde ara...")
            self.load_requests_from_server()

    def on_search_change(self, event=None):
        query = self.search_entry.get().strip() if self.search_entry else ""
        if self.active_sub_tab == "notes":
            self.load_notes_from_server(query=query)
        else:
            self.load_requests_from_server(query=query)

    def on_sort_change(self, choice=None):
        query = self.search_entry.get().strip() if self.search_entry else ""
        self.load_notes_from_server(query=query)

    # ==========================================
    # DERS NOTLARI MANTIĞI & PARLAYAN KENARLIKLAR
    # ==========================================
    def load_notes_from_server(self, query=""):
        p = self.app.current_palette
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        try:
            response = server_interaction.send_get_all_notes()

            if isinstance(response, dict) and response.get("status") == "success":
                notes_data = response.get("notes", [])

                if query:
                    q = query.lower()
                    notes_data = [
                        n for n in notes_data
                        if q in n.get("title", "").lower() or q in n.get("author", "").lower()
                    ]

                sort_by = self.sort_option.get() if self.sort_option else "❤️ Beğeniye Göre"

                if sort_by == "❤️ Beğeniye Göre":
                    notes_data.sort(key=lambda n: int(n.get("likes", 0)), reverse=True)
                elif sort_by == "📅 Tarihe Göre (En Yeni)":
                    notes_data.sort(key=lambda n: int(n.get("id", 0)), reverse=True)
                elif sort_by == "🔤 A'dan Z'ye":
                    notes_data.sort(key=lambda n: n.get("title", "").lower())
                elif sort_by == "🔤 Z'den A'ya":
                    notes_data.sort(key=lambda n: n.get("title", "").lower(), reverse=True)

                if not notes_data:
                    msg = "Aramanızla eşleşen ders notu bulunamadı." if query else "Henüz ders notu yüklenmemiş. İlk notu sen ekle!"
                    lbl = ctk.CTkLabel(self.scroll_frame, text=msg, text_color=p["text_sub"], font=ctk.CTkFont(size=13))
                    lbl.pack(pady=40)
                    return

                for note in notes_data:
                    note_id = note.get("id", "")
                    note_title = note.get("title", "İsimsiz Not")
                    note_likes = str(note.get("likes", "0"))
                    note_author = note.get("author", "Bilinmiyor")
                    note_date = note.get("date", "Bilinmiyor")
                    note_file = note.get("file_name", "")

                    file_badge = " 📎" if note_file else ""

                    card = ctk.CTkFrame(self.scroll_frame, fg_color=p["card"], corner_radius=10, border_width=1, border_color="#313244", height=50)
                    card.pack(fill="x", padx=10, pady=6)
                    card.pack_propagate(False)

                    title_btn = ctk.CTkButton(
                        card,
                        text=f"  ◆  {note_title}{file_badge}  •  Yazan: {note_author}  •  📅 {note_date}  (❤️ {note_likes})",
                        fg_color="transparent",
                        hover_color=p["entry"],
                        text_color=p["text_main"],
                        anchor="w",
                        font=ctk.CTkFont(size=13, weight="bold"),
                        corner_radius=8,
                        command=lambda nid=note_id: self.open_note_detail(nid)
                    )
                    title_btn.pack(fill="both", expand=True, padx=2, pady=2)

                    def make_hover(c_widget):
                        def on_enter(e):
                            c_widget.configure(border_color=p["accent"])
                        def on_leave(e):
                            c_widget.configure(border_color="#313244")
                        return on_enter, on_leave

                    enter_fn, leave_fn = make_hover(card)
                    title_btn.bind("<Enter>", enter_fn)
                    title_btn.bind("<Leave>", leave_fn)

            else:
                err_msg = response.get("message", "Notlar yüklenirken hata oluştu.") if isinstance(response, dict) else "Notlar yüklenemedi."
                lbl = ctk.CTkLabel(self.scroll_frame, text=err_msg, text_color="#F38BA8", font=ctk.CTkFont(size=13))
                lbl.pack(pady=40)

        except Exception as e:
            print(f"[ERROR] {e}")
            lbl = ctk.CTkLabel(self.scroll_frame, text="Sunucuya bağlanılamadı!", text_color="#F38BA8", font=ctk.CTkFont(size=13))
            lbl.pack(pady=40)

    def open_note_detail(self, note_id):
        p = self.app.current_palette
        response = server_interaction.send_get_note(note_id, self.current_username)

        detail_modal = ctk.CTkToplevel(self)
        detail_modal.title("Ders Notu Detayı")
        detail_modal.geometry("460x520")
        detail_modal.resizable(False, False)
        detail_modal.configure(fg_color=p["bg"])
        detail_modal.grab_set()

        if isinstance(response, dict) and response.get("status") == "success":
            note = response.get("note", {})
            title = note.get("title", "İsimsiz")
            content = note.get("content", "")
            likes = note.get("likes", 0)
            author = note.get("author", "Bilinmiyor")
            date = note.get("date", "Bilinmiyor")
            file_name = note.get("file_name", "")
            file_size = note.get("file_size", "")
            is_liked = note.get("is_liked", False)

            lbl_title = ctk.CTkLabel(detail_modal, text=title, font=ctk.CTkFont(size=20, weight="bold"), text_color=p["accent"])
            lbl_title.pack(padx=30, pady=(20, 5), anchor="w")

            lbl_author = ctk.CTkLabel(detail_modal, text=f"◆ Paylaşan: {author}  •  📅 {date}", font=ctk.CTkFont(size=12, weight="bold"), text_color=p["text_sub"])
            lbl_author.pack(padx=30, anchor="w", pady=(0, 10))

            txt_content = ctk.CTkTextbox(detail_modal, width=400, height=120, fg_color=p["entry"], text_color=p["text_main"], font=ctk.CTkFont(size=13))
            txt_content.pack(padx=30, pady=5)
            txt_content.insert("0.0", content)
            txt_content.configure(state="disabled")

            info_lbl = ctk.CTkLabel(detail_modal, text="", font=ctk.CTkFont(size=11), text_color=p["text_sub"])
            info_lbl.pack(pady=(2, 2))

            if file_name:
                size_str = f"  •  💾 {file_size}" if file_size else ""

                file_frame = ctk.CTkFrame(detail_modal, fg_color=p["entry"], corner_radius=8, border_width=1, border_color="#313244")
                file_frame.pack(fill="x", padx=30, pady=8)

                lbl_file = ctk.CTkLabel(
                    file_frame,
                    text=f"📎 {file_name}{size_str}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=p["text_main"]
                )
                lbl_file.pack(side="left", padx=12, pady=8)

                def download_action():
                    save_path = save_native_file_dialog(initialfile=file_name, title="Dosyayı Kaydet")
                    if save_path:
                        dl_res = server_interaction.send_download_file(note_id)
                        if isinstance(dl_res, dict) and dl_res.get("status") == "success":
                            file_b64 = dl_res.get("file_data", "")
                            try:
                                with open(save_path, "wb") as f:
                                    f.write(base64.b64decode(file_b64))
                                info_lbl.configure(text_color="#A6E3A1", text="✅ Dosya başarıyla indirildi!")
                            except Exception as ex:
                                info_lbl.configure(text_color="#F38BA8", text=f"❌ Dosya yazma hatası: {ex}")
                        else:
                            err = dl_res.get("message", "İndirilemedi") if isinstance(dl_res, dict) else "Hata"
                            info_lbl.configure(text_color="#F38BA8", text=f"❌ {err}")

                btn_download = ctk.CTkButton(
                    file_frame,
                    text="📥 İndir",
                    width=85,
                    height=30,
                    fg_color=p["accent"],
                    hover_color=p["hover"],
                    text_color="#11111B",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    corner_radius=6,
                    command=download_action
                )
                btn_download.pack(side="right", padx=10, pady=6)

            action_frame = ctk.CTkFrame(detail_modal, fg_color="transparent")
            action_frame.pack(fill="x", padx=30, pady=(10, 10))

            lbl_likes = ctk.CTkLabel(action_frame, text=f"❤️ {likes} Beğeni", font=ctk.CTkFont(size=13, weight="bold"), text_color=p["text_main"])
            lbl_likes.pack(side="left")

            right_btn_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
            right_btn_frame.pack(side="right")

            # 🗑️ SADECE NOT SAHİBİ GÖRÜR
            if str(author).strip() == str(self.current_username).strip():
                def delete_note_action():
                    res = server_interaction.send_delete_note(self.current_username, note_id)
                    if isinstance(res, dict) and res.get("status") == "success":
                        detail_modal.destroy()
                        q = self.search_entry.get().strip() if self.search_entry else ""
                        self.load_notes_from_server(query=q)
                    else:
                        err = res.get("message", "Silinemedi") if isinstance(res, dict) else "Hata"
                        info_lbl.configure(text_color="#F38BA8", text=f"❌ {err}")

                btn_delete = ctk.CTkButton(
                    right_btn_frame,
                    text="🗑️ Notu Sil",
                    width=95,
                    height=32,
                    fg_color="#F38BA8",
                    hover_color="#EBA0AC",
                    text_color="#11111B",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    corner_radius=8,
                    command=delete_note_action
                )
                btn_delete.pack(side="left", padx=(0, 8))

            def like_action():
                res = server_interaction.send_like_note(self.current_username, note_id)

                if isinstance(res, dict) and res.get("status") == "success":
                    new_likes = res.get("likes", 0)
                    action = res.get("action")
                    lbl_likes.configure(text=f"❤️ {new_likes} Beğeni")

                    if action == "liked":
                        like_btn.configure(text="💔 Vazgeç", fg_color="#F38BA8", hover_color="#EBA0AC")
                        info_lbl.configure(text_color="#A6E3A1", text="✅ Notu beğendiniz!")
                    else:
                        like_btn.configure(text="❤️ Beğen", fg_color=p["accent"], hover_color=p["hover"])
                        info_lbl.configure(text_color="#A6ADC8", text="ℹ️ Beğeni geri çekildi.")

                    query = self.search_entry.get().strip() if self.search_entry else ""
                    self.load_notes_from_server(query=query)
                else:
                    err_msg = res.get("message", "İşlem başarısız") if isinstance(res, dict) else "Hata oluştu"
                    info_lbl.configure(text_color="#F38BA8", text=f"⚠️ {err_msg}")

            initial_btn_text = "💔 Vazgeç" if is_liked else "❤️ Beğen"
            initial_btn_fg = "#F38BA8" if is_liked else p["accent"]
            initial_btn_hover = "#EBA0AC" if is_liked else p["hover"]

            like_btn = ctk.CTkButton(
                right_btn_frame,
                text=initial_btn_text,
                width=100,
                height=32,
                fg_color=initial_btn_fg,
                hover_color=initial_btn_hover,
                text_color="#11111B",
                font=ctk.CTkFont(size=12, weight="bold"),
                corner_radius=8,
                command=like_action
            )
            like_btn.pack(side="left")

        else:
            err_msg = response.get("message", "Not detayları alınamadı!") if isinstance(response, dict) else "Not detayları alınamadı!"
            err_lbl = ctk.CTkLabel(detail_modal, text=err_msg, text_color="#F38BA8", font=ctk.CTkFont(size=14))
            err_lbl.pack(padx=30, pady=50)

    def open_add_note_modal(self):
        p = self.app.current_palette
        self.selected_file_path = None
        placeholder_note = "Not içeriğini buraya yazın..."

        modal = ctk.CTkToplevel(self)
        modal.title("Yeni Ders Notu Ekle")
        modal.geometry("420x530")
        modal.resizable(False, False)
        modal.configure(fg_color=p["bg"])
        modal.grab_set()

        title_lbl = ctk.CTkLabel(modal, text="📖 Yeni Not Paylaş", font=ctk.CTkFont(size=18, weight="bold"), text_color=p["text_main"])
        title_lbl.pack(pady=(20, 10))

        self.note_title_entry = ctk.CTkEntry(
            modal,
            placeholder_text="Not Başlığı (Örn: Matematik Vize)",
            width=340,
            height=38,
            fg_color=p["entry"],
            border_color="#313244",
            text_color=p["text_main"]
        )
        self.note_title_entry.pack(pady=8)

        self.note_content_text = ctk.CTkTextbox(
            modal,
            width=340,
            height=130,
            fg_color=p["entry"],
            border_color="#313244",
            text_color=p["text_sub"]
        )
        self.note_content_text.pack(pady=8)
        self.note_content_text.insert("0.0", placeholder_note)

        # 🎯 TIKLANINCA SİLİNEN AKILLI PLACEHOLDER
        def on_note_focus_in(event):
            if self.note_content_text.get("0.0", "end-1c") == placeholder_note:
                self.note_content_text.delete("0.0", "end")
                self.note_content_text.configure(text_color=p["text_main"])

        def on_note_focus_out(event):
            if not self.note_content_text.get("0.0", "end-1c").strip():
                self.note_content_text.insert("0.0", placeholder_note)
                self.note_content_text.configure(text_color=p["text_sub"])

        self.note_content_text.bind("<FocusIn>", on_note_focus_in)
        self.note_content_text.bind("<FocusOut>", on_note_focus_out)

        file_select_frame = ctk.CTkFrame(modal, fg_color="transparent")
        file_select_frame.pack(pady=6)

        def select_file():
            file_path = open_native_file_dialog(title="Eklenecek Dosyayı Seçin")
            if file_path:
                self.selected_file_path = file_path
                file_name = os.path.basename(file_path)
                self.selected_file_label.configure(text=f"📎 {file_name}", text_color=p["accent"])

        btn_select_file = ctk.CTkButton(
            file_select_frame,
            text="📁 Dosya Seç",
            width=110,
            height=32,
            fg_color=p["entry"],
            hover_color=p["hover"],
            text_color=p["text_main"],
            corner_radius=8,
            command=select_file
        )
        btn_select_file.pack(side="left", padx=(0, 10))

        self.selected_file_label = ctk.CTkLabel(
            file_select_frame,
            text="Dosya seçilmedi (İsteğe bağlı)",
            font=ctk.CTkFont(size=11),
            text_color=p["text_sub"]
        )
        self.selected_file_label.pack(side="left")

        self.modal_info_lbl = ctk.CTkLabel(modal, text="", font=ctk.CTkFont(size=12), text_color=p["text_sub"])
        self.modal_info_lbl.pack(pady=4)

        save_btn = ctk.CTkButton(
            modal,
            text="Notu Kaydet",
            width=340,
            height=40,
            fg_color=p["accent"],
            hover_color=p["hover"],
            text_color="#11111B",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self.save_note_to_server(modal, save_btn, placeholder_note)
        )
        save_btn.pack(pady=12)

    def save_note_to_server(self, modal_window, save_btn, placeholder_text):
        title = self.note_title_entry.get().strip()
        content = self.note_content_text.get("0.0", "end-1c").strip()
        author = self.current_username

        if not title or not content or content == placeholder_text:
            self.modal_info_lbl.configure(text_color="#F38BA8", text="⚠️ Lütfen tüm alanları doldurun!")
            return

        save_btn.configure(state="disabled", text="⏳ Yükleniyor...")
        modal_window.update_idletasks()

        file_name = None
        file_data = None

        if self.selected_file_path and os.path.exists(self.selected_file_path):
            try:
                file_name = os.path.basename(self.selected_file_path)
                with open(self.selected_file_path, "rb") as f:
                    file_bytes = f.read()
                file_data = base64.b64encode(file_bytes).decode('utf-8')
            except Exception as e:
                self.modal_info_lbl.configure(text_color="#F38BA8", text=f"Dosya okunamadı: {e}")
                save_btn.configure(state="normal", text="Notu Kaydet")
                return

        try:
            response = server_interaction.send_create_note(author, title, content, file_name, file_data)

            if isinstance(response, dict) and response.get("status") == "success":
                self.modal_info_lbl.configure(text_color="#A6E3A1", text="✅ Not başarıyla kaydedildi!")
                modal_window.after(800, modal_window.destroy)
                query = self.search_entry.get().strip() if self.search_entry else ""
                self.load_notes_from_server(query=query)
            else:
                error_msg = response.get("message", "Kayıt başarısız") if isinstance(response, dict) else "Kayıt başarısız"
                self.modal_info_lbl.configure(text_color="#F38BA8", text=f"❌ {error_msg}")
                save_btn.configure(state="normal", text="Notu Kaydet")

        except Exception as e:
            self.modal_info_lbl.configure(text_color="#F38BA8", text="❌ Sunucuya bağlanılamadı!")
            print(f"[NETWORK ERROR] {e}")
            save_btn.configure(state="normal", text="Notu Kaydet")

    # ==========================================
    # NOT İSTEKLERİ & SCROLLBAR YORUMLAR
    # ==========================================
    def load_requests_from_server(self, query=""):
        p = self.app.current_palette
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        try:
            response = server_interaction.send_get_all_requests()

            if isinstance(response, dict) and response.get("status") == "success":
                requests_data = response.get("requests", [])

                if query:
                    q = query.lower()
                    requests_data = [
                        r for r in requests_data
                        if q in r.get("title", "").lower() or q in r.get("author", "").lower() or q in r.get("content", "").lower()
                    ]

                if not requests_data:
                    msg = "Aramanızla eşleşen istek bulunamadı." if query else "Henüz ders notu isteği açılmamış. İlk isteği sen aç!"
                    lbl = ctk.CTkLabel(self.scroll_frame, text=msg, text_color=p["text_sub"], font=ctk.CTkFont(size=13))
                    lbl.pack(pady=40)
                    return

                for req in requests_data:
                    req_id = req.get("id")
                    title = req.get("title", "İsimsiz İstek")
                    content = req.get("content", "")
                    author = req.get("author", "Bilinmiyor")
                    date = req.get("date", "Bilinmiyor")
                    comments = req.get("comments", [])

                    card = ctk.CTkFrame(self.scroll_frame, fg_color=p["card"], corner_radius=10, border_width=1, border_color="#313244")
                    card.pack(fill="x", padx=10, pady=8)

                    header_box = ctk.CTkFrame(card, fg_color="transparent")
                    header_box.pack(fill="x", padx=15, pady=(12, 5))

                    lbl_req_title = ctk.CTkLabel(header_box, text=f"🙋‍♂️ {title}", font=ctk.CTkFont(size=15, weight="bold"), text_color=p["accent"])
                    lbl_req_title.pack(side="left")

                    right_info_box = ctk.CTkFrame(header_box, fg_color="transparent")
                    right_info_box.pack(side="right")

                    lbl_req_info = ctk.CTkLabel(right_info_box, text=f"İsteyen: {author}  •  📅 {date}", font=ctk.CTkFont(size=11), text_color=p["text_sub"])
                    lbl_req_info.pack(side="left", padx=(0, 10))

                    # 🎯 SADECE İSTEĞİ AÇAN KULLANICI GÖRÜR
                    if str(author).strip() == str(self.current_username).strip():
                        def delete_request_action(rid=req_id):
                            res = server_interaction.send_delete_request(self.current_username, rid)
                            if isinstance(res, dict) and res.get("status") == "success":
                                q = self.search_entry.get().strip() if self.search_entry else ""
                                self.load_requests_from_server(query=q)

                        btn_end_req = ctk.CTkButton(
                            right_info_box,
                            text="❌ İsteği Sonlandır",
                            height=26,
                            fg_color="#F38BA8",
                            hover_color="#EBA0AC",
                            text_color="#11111B",
                            font=ctk.CTkFont(size=11, weight="bold"),
                            corner_radius=6,
                            command=delete_request_action
                        )
                        btn_end_req.pack(side="left")

                    lbl_content = ctk.CTkLabel(card, text=content, font=ctk.CTkFont(size=13), text_color=p["text_main"], anchor="w", justify="left", wraplength=520)
                    lbl_content.pack(fill="x", padx=15, pady=(0, 10))

                    comments_container = ctk.CTkFrame(card, fg_color=p["entry"], corner_radius=8)
                    comments_container.pack(fill="x", padx=15, pady=(5, 12))

                    lbl_comm_title = ctk.CTkLabel(comments_container, text=f"💬 Yorumlar ({len(comments)})", font=ctk.CTkFont(size=12, weight="bold"), text_color=p["text_sub"])
                    lbl_comm_title.pack(anchor="w", padx=12, pady=(8, 4))

                    # 📜 YORUMLAR İÇİN SABİT YÜKSEKLİKLİ KAYDIRMA ÇUBUĞU
                    if comments:
                        comm_scroll = ctk.CTkScrollableFrame(
                            comments_container,
                            height=110,
                            fg_color="transparent"
                        )
                        comm_scroll.pack(fill="x", padx=10, pady=(0, 5))

                        for c in comments:
                            c_author = c.get("author", "Bilinmiyor")
                            c_text = c.get("content", "")
                            c_date = c.get("date", "")

                            c_frame = ctk.CTkFrame(comm_scroll, fg_color="transparent")
                            c_frame.pack(fill="x", padx=5, pady=2)

                            c_lbl = ctk.CTkLabel(
                                c_frame,
                                text=f"• {c_author}: {c_text}  ({c_date})",
                                font=ctk.CTkFont(size=12),
                                text_color=p["text_main"],
                                anchor="w",
                                justify="left",
                                wraplength=480
                            )
                            c_lbl.pack(anchor="w")

                    add_comm_frame = ctk.CTkFrame(comments_container, fg_color="transparent")
                    add_comm_frame.pack(fill="x", padx=10, pady=8)

                    comm_entry = ctk.CTkEntry(
                        add_comm_frame,
                        placeholder_text="Bir yanıt / yorum yazın...",
                        height=32,
                        fg_color=p["card"],
                        border_color="#313244",
                        text_color=p["text_main"],
                        corner_radius=6
                    )
                    comm_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

                    def post_comment(rid=req_id, entry_widget=comm_entry):
                        text = entry_widget.get().strip()
                        if text:
                            res = server_interaction.send_add_comment(self.current_username, rid, text)
                            if isinstance(res, dict) and res.get("status") == "success":
                                q = self.search_entry.get().strip() if self.search_entry else ""
                                self.load_requests_from_server(query=q)

                    btn_send_comm = ctk.CTkButton(
                        add_comm_frame,
                        text="Gönder",
                        width=75,
                        height=32,
                        fg_color=p["accent"],
                        hover_color=p["hover"],
                        text_color="#11111B",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        corner_radius=6,
                        command=post_comment
                    )
                    btn_send_comm.pack(side="right")

            else:
                lbl = ctk.CTkLabel(self.scroll_frame, text="İstekler yüklenemedi.", text_color="#F38BA8", font=ctk.CTkFont(size=13))
                lbl.pack(pady=40)

        except Exception as e:
            print(f"[REQUEST ERROR] {e}")
            lbl = ctk.CTkLabel(self.scroll_frame, text="Sunucuya bağlanılamadı!", text_color="#F38BA8", font=ctk.CTkFont(size=13))
            lbl.pack(pady=40)

    def open_add_request_modal(self):
        p = self.app.current_palette
        placeholder_req = "Hangi ders, hangi konular veya detaylar gerektiğini buraya yazın..."

        modal = ctk.CTkToplevel(self)
        modal.title("Yeni Not İsteği Ekle")
        modal.geometry("420x420")
        modal.resizable(False, False)
        modal.configure(fg_color=p["bg"])
        modal.grab_set()

        title_lbl = ctk.CTkLabel(modal, text="🙋‍♂️ Yeni Ders Notu İste", font=ctk.CTkFont(size=18, weight="bold"), text_color=p["text_main"])
        title_lbl.pack(pady=(20, 10))

        req_title_entry = ctk.CTkEntry(
            modal,
            placeholder_text="İstek Başlığı (Max 60 Karakter)",
            width=340,
            height=38,
            fg_color=p["entry"],
            border_color="#313244",
            text_color=p["text_main"]
        )
        req_title_entry.pack(pady=8)

        req_content_text = ctk.CTkTextbox(
            modal,
            width=340,
            height=140,
            fg_color=p["entry"],
            border_color="#313244",
            text_color=p["text_sub"]
        )
        req_content_text.pack(pady=8)
        req_content_text.insert("0.0", placeholder_req)

        # 🎯 CANLI DİNAMİK PLACEHOLDER
        def on_req_focus_in(event):
            if req_content_text.get("0.0", "end-1c") == placeholder_req:
                req_content_text.delete("0.0", "end")
                req_content_text.configure(text_color=p["text_main"])

        def on_req_focus_out(event):
            if not req_content_text.get("0.0", "end-1c").strip():
                req_content_text.insert("0.0", placeholder_req)
                req_content_text.configure(text_color=p["text_sub"])

        req_content_text.bind("<FocusIn>", on_req_focus_in)
        req_content_text.bind("<FocusOut>", on_req_focus_out)

        modal_info_lbl = ctk.CTkLabel(modal, text="Başlık max 60, açıklama max 250 karakter olmalıdır.", font=ctk.CTkFont(size=11), text_color=p["text_sub"])
        modal_info_lbl.pack(pady=4)

        def save_request():
            t = req_title_entry.get().strip()
            c = req_content_text.get("0.0", "end-1c").strip()

            if not t or not c or c == placeholder_req:
                modal_info_lbl.configure(text_color="#F38BA8", text="⚠️ Lütfen tüm alanları doldurun!")
                return

            if len(t) > 60:
                modal_info_lbl.configure(text_color="#F38BA8", text="⚠️ İstek başlığı en fazla 60 karakter olabilir!")
                return

            if len(c) > 250:
                modal_info_lbl.configure(text_color="#F38BA8", text="⚠️ Açıklama en fazla 250 karakter olabilir!")
                return

            res = server_interaction.send_create_request(self.current_username, t, c)
            if isinstance(res, dict) and res.get("status") == "success":
                modal_info_lbl.configure(text_color="#A6E3A1", text="✅ İstek başarıyla oluşturuldu!")
                modal.after(800, modal.destroy)
                q = self.search_entry.get().strip() if self.search_entry else ""
                self.load_requests_from_server(query=q)
            else:
                err = res.get("message", "Hata oluştu") if isinstance(res, dict) else "Hata"
                modal_info_lbl.configure(text_color="#F38BA8", text=f"❌ {err}")

        btn_save_req = ctk.CTkButton(
            modal,
            text="İsteği Paylaş",
            width=340,
            height=40,
            fg_color=p["accent"],
            hover_color=p["hover"],
            text_color="#11111B",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=save_request
        )
        btn_save_req.pack(pady=12)

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

    def open_social(self):
        self.clear_display()
        p = self.app.current_palette
        self.display_card.grid_rowconfigure(0, weight=1)
        self.display_card.grid_columnconfigure(0, weight=1)
        lbl = ctk.CTkLabel(
            self.display_card,
            text="👥 Kampüs Sosyal Akışı\nDiğer öğrencilerle etkileşime geçin, paylaşımları takip edin.",
            font=ctk.CTkFont(size=15),
            text_color=p["text_main"]
        )
        lbl.grid(row=0, column=0)

    def open_profile(self):
        self.clear_display()
        p = self.app.current_palette
        self.display_card.grid_rowconfigure(0, weight=1)
        self.display_card.grid_columnconfigure(0, weight=1)

        profile_box = ctk.CTkFrame(self.display_card, fg_color="transparent")
        profile_box.grid(row=0, column=0, padx=40, pady=40, sticky="nw")

        lbl_title = ctk.CTkLabel(
            profile_box,
            text=f"👤 Profil Detayları: {self.current_username}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=p["text_main"]
        )
        lbl_title.pack(anchor="w", pady=(0, 15))

        lbl_info = ctk.CTkLabel(
            profile_box,
            text=f"• Kullanıcı Adı: {self.current_username}\n• Rol: Öğrenci\n• Hesap Durumu: Aktif",
            font=ctk.CTkFont(size=14),
            text_color=p["text_sub"],
            justify="left"
        )
        lbl_info.pack(anchor="w")

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
        self.profile_btn.configure(fg_color=p["entry"], hover_color=p["hover"], text_color=p["accent"])
        self.welcome_title.configure(text_color=p["text_main"])

        if hasattr(self, "info_text") and self.info_text.winfo_exists():
            self.info_text.configure(text_color=p["text_sub"])

        for btn in self.sidebar_buttons:
            btn.configure(text_color=p["text_main"], hover_color=p["entry"])

        if hasattr(self, "action_btn") and self.action_btn is not None and self.action_btn.winfo_exists():
            self.action_btn.configure(fg_color=p["accent"], hover_color=p["hover"])

        if hasattr(self, "sub_tab_segment") and self.sub_tab_segment is not None and self.sub_tab_segment.winfo_exists():
            self.sub_tab_segment.configure(selected_color=p["accent"], selected_hover_color=p["hover"], unselected_color=p["entry"], text_color=p["text_main"])

        if hasattr(self, "settings_container") and self.settings_container is not None:
            try:
                if self.settings_container.winfo_exists():
                    children = self.display_card.winfo_children()
                    if children and children[0] == self.settings_container:
                        self.open_settings()
            except Exception:
                pass
