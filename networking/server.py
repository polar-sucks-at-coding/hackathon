import os
import sys
import json
import threading
import datetime
import base64
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS

# Proje dizin yapılandırması
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'notes'))

from notes.note import Note
from user import User
from user_profile import Profile

app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')
CORS(app)  # Cross-Origin İstekleri Etkinleştir

HOST = '0.0.0.0'
PORT = 5000
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOADS_DIR = os.path.join(DATA_DIR, 'uploads')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

ACCOUNTS_FILE = os.path.join(DATA_DIR, 'accounts.txt')
NOTES_FILE = os.path.join(DATA_DIR, 'notes.txt')
NEXT_ID_FILE = os.path.join(DATA_DIR, 'next_id.txt')
LIKES_FILE = os.path.join(DATA_DIR, 'likes.txt')
PROFILES_FILE = os.path.join(DATA_DIR, 'user_profiles.txt')
REQUESTS_FILE = os.path.join(DATA_DIR, 'requests.json')

users = {}
notes = {}
user_likes = {}
requests_data = {}
next_note_id = 1
next_request_id = 1
lock = threading.Lock()


def get_formatted_file_size(file_path):
    if not os.path.exists(file_path):
        return ""
    size_bytes = os.path.getsize(file_path)
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def load_data():
    global next_note_id, next_request_id, users, notes, user_likes, requests_data

    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                user = User.from_string(line)
                if user:
                    users[user.username] = user

    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                profile = Profile.from_string(line)
                if profile and profile.username in users:
                    users[profile.username].profile = profile

    if os.path.exists(NEXT_ID_FILE):
        with open(NEXT_ID_FILE, 'r', encoding='utf-8') as f:
            try:
                next_note_id = int(f.read().strip())
            except ValueError:
                next_note_id = 1

    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                note = Note.from_string(line)
                if note:
                    notes[note.id] = note

    if os.path.exists(LIKES_FILE):
        with open(LIKES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2:
                    user_likes[(parts[0], int(parts[1]))] = True

    if os.path.exists(REQUESTS_FILE):
        try:
            with open(REQUESTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                requests_data = {int(k): v for k, v in data.get("requests", {}).items()}
                next_request_id = data.get("next_id", 1)
        except Exception as e:
            print(f"[LOAD REQUESTS ERROR] {e}")


def save_accounts():
    with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
        for user in users.values():
            f.write(user.to_string() + '\n')


def save_profiles():
    with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
        for user in users.values():
            f.write(user.profile.to_string() + '\n')


def save_notes():
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        for note in notes.values():
            f.write(note.to_string() + '\n')


def save_next_id():
    with open(NEXT_ID_FILE, 'w', encoding='utf-8') as f:
        f.write(str(next_note_id))


def save_likes():
    with open(LIKES_FILE, 'w', encoding='utf-8') as f:
        for (username, note_id) in user_likes.keys():
            f.write(f"{username}|{note_id}\n")


def save_requests():
    try:
        with open(REQUESTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"requests": requests_data, "next_id": next_request_id}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[SAVE REQUESTS ERROR] {e}")


# ==========================================
# WEBSİTE VE ARAYÜZ YÖNLENDİRMELERİ
# ==========================================

@app.route('/')
def index():
    """Ana HTML Arayüzünü Sunar"""
    index_path = os.path.join(BASE_DIR, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    return "index.html dosyası bulunamadı!", 404


@app.route('/logo.jpeg')
def logo():
    logo_path = os.path.join(BASE_DIR, 'logo.jpeg')
    if os.path.exists(logo_path):
        return send_file(logo_path)
    return "", 404


# ==========================================
# REST API ENDPOINTLERİ
# ==========================================

@app.route('/api/command', methods=['POST'])
def handle_command():
    request_data = request.get_json(force=True, silent=True) or {}
    command = request_data.get('command')

    if command == 'REGISTER':
        return jsonify(handle_register(request_data))
    elif command == 'LOGIN':
        return jsonify(handle_login(request_data))
    elif command == 'LOGOUT':
        return jsonify(handle_logout(request_data))
    elif command == 'CREATE_NOTE':
        return jsonify(handle_create_note(request_data))
    elif command == 'GET_NOTE':
        return jsonify(handle_get_note(request_data))
    elif command == 'DELETE_NOTE':
        return jsonify(handle_delete_note(request_data))
    elif command == 'GET_ALL_NOTES':
        return jsonify(handle_get_all_notes(request_data))
    elif command == 'LIKE_NOTE':
        return jsonify(handle_like_note(request_data))
    elif command == 'DOWNLOAD_FILE':
        return jsonify(handle_download_file(request_data))
    elif command == 'CREATE_REQUEST':
        return jsonify(handle_create_request(request_data))
    elif command == 'DELETE_REQUEST':
        return jsonify(handle_delete_request(request_data))
    elif command == 'GET_ALL_REQUESTS':
        return jsonify(handle_get_all_requests(request_data))
    elif command == 'ADD_COMMENT':
        return jsonify(handle_add_comment(request_data))
    else:
        return jsonify({"status": "error", "message": "Bilinmeyen komut"})


# ==========================================
# İŞ MANTIĞI FONKSİYONLARI
# ==========================================

def handle_register(data):
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {"status": "error", "message": "Kullanıcı adı ve şifre gerekli"}

    with lock:
        if username in users:
            return {"status": "error", "message": "Bu kullanıcı adı zaten alınmış"}

        user = User(username, password, Profile(username))
        users[username] = user
        save_accounts()
        save_profiles()
        return {"status": "success", "message": "Hesap başarıyla oluşturuldu"}


def handle_login(data):
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {"status": "error", "message": "Kullanıcı adı ve şifre gerekli"}

    with lock:
        if username not in users:
            return {"status": "error", "message": "Kullanıcı bulunamadı"}

        if users[username].password != password:
            return {"status": "error", "message": "Hatalı şifre"}

        return {"status": "success", "message": "Giriş başarılı"}


def handle_logout(data):
    return {"status": "success", "message": "Çıkış yapıldı"}


def handle_create_note(data):
    username = data.get('username')
    title = data.get('title')
    content = data.get('content')
    file_name = data.get('file_name', '')
    file_b64 = data.get('file_data', '')

    if not username or not title or not content:
        return {"status": "error", "message": "Tüm alanlar doldurulmalıdır"}

    with lock:
        if username not in users:
            return {"status": "error", "message": "Kullanıcı bulunamadı"}

        global next_note_id
        now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        saved_file_name = ""

        if file_name and file_b64:
            try:
                file_bytes = base64.b64decode(file_b64)
                disk_file_name = f"{next_note_id}_{file_name}"
                file_path = os.path.join(UPLOADS_DIR, disk_file_name)
                with open(file_path, 'wb') as f:
                    f.write(file_bytes)
                saved_file_name = file_name
            except Exception as e:
                print(f"[FILE SAVE ERROR] {e}")

        note = Note(next_note_id, title, content, username, date=now_str, file_name=saved_file_name)
        notes[next_note_id] = note
        users[username].profile.add_note(next_note_id)
        next_note_id += 1

        save_notes()
        save_next_id()
        save_profiles()

        return {"status": "success", "message": "Not paylaşıldı", "note_id": note.id}


def handle_get_note(data):
    note_id = data.get('note_id')
    username = data.get('username')

    if note_id is None:
        return {"status": "error", "message": "Not ID gerekli"}

    note_id = int(note_id)

    with lock:
        if note_id not in notes:
            return {"status": "error", "message": "Not bulunamadı"}

        note = notes[note_id]
        is_liked = (username, note_id) in user_likes if username else False

        file_name = getattr(note, 'file_name', '')
        file_size = ""
        if file_name:
            file_path = os.path.join(UPLOADS_DIR, f"{note.id}_{file_name}")
            file_size = get_formatted_file_size(file_path)

        return {
            "status": "success",
            "note": {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "author": note.author,
                "likes": note.likes,
                "date": getattr(note, 'date', 'Bilinmiyor'),
                "file_name": file_name,
                "file_size": file_size,
                "is_liked": is_liked
            }
        }


def handle_delete_note(data):
    username = data.get('username')
    note_id = data.get('note_id')

    if not username or note_id is None:
        return {"status": "error", "message": "Parametreler eksik"}

    note_id = int(note_id)
    with lock:
        if note_id not in notes:
            return {"status": "error", "message": "Not bulunamadı"}

        if str(notes[note_id].author).strip() != str(username).strip():
            return {"status": "error", "message": "Bu notu silme yetkiniz yok!"}

        note = notes[note_id]
        if getattr(note, 'file_name', ''):
            file_path = os.path.join(UPLOADS_DIR, f"{note.id}_{note.file_name}")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"[FILE REMOVE ERROR] {e}")

        del notes[note_id]

        to_del = [k for k in user_likes.keys() if k[1] == note_id]
        for k in to_del:
            del user_likes[k]

        save_notes()
        save_likes()
        return {"status": "success", "message": "Not silindi"}


def handle_download_file(data):
    note_id = data.get('note_id')
    if note_id is None:
        return {"status": "error", "message": "Not ID gerekli"}

    note_id = int(note_id)

    with lock:
        if note_id not in notes:
            return {"status": "error", "message": "Not bulunamadı"}

        note = notes[note_id]
        if not getattr(note, 'file_name', ''):
            return {"status": "error", "message": "Bu not için ekli dosya bulunmuyor."}

        file_path = os.path.join(UPLOADS_DIR, f"{note.id}_{note.file_name}")
        if not os.path.exists(file_path):
            return {"status": "error", "message": "Sunucuda dosya bulunamadı."}

        try:
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            file_b64 = base64.b64encode(file_bytes).decode('utf-8')
            return {
                "status": "success",
                "file_name": note.file_name,
                "file_data": file_b64
            }
        except Exception as e:
            return {"status": "error", "message": f"Dosya okuma hatası: {str(e)}"}


def handle_like_note(data):
    username = data.get('username')
    note_id = data.get('note_id')

    if not username or note_id is None:
        return {"status": "error", "message": "Kullanıcı adı ve Not ID gerekli"}

    note_id = int(note_id)

    with lock:
        if username not in users:
            return {"status": "error", "message": "Kullanıcı bulunamadı"}

        if note_id not in notes:
            return {"status": "error", "message": "Not bulunamadı"}

        if (username, note_id) in user_likes:
            del user_likes[(username, note_id)]
            notes[note_id].likes = max(0, notes[note_id].likes - 1)
            save_notes()
            save_likes()
            return {
                "status": "success",
                "action": "unliked",
                "message": "Beğeni geri çekildi",
                "likes": notes[note_id].likes
            }
        else:
            user_likes[(username, note_id)] = True
            notes[note_id].likes += 1
            save_notes()
            save_likes()
            return {
                "status": "success",
                "action": "liked",
                "message": "Not beğenildi",
                "likes": notes[note_id].likes
            }


def handle_get_all_notes(data):
    with lock:
        notes_list = []
        for note in notes.values():
            file_name = getattr(note, 'file_name', '')
            file_size = ""
            if file_name:
                file_path = os.path.join(UPLOADS_DIR, f"{note.id}_{file_name}")
                file_size = get_formatted_file_size(file_path)

            notes_list.append({
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "author": note.author,
                "likes": note.likes,
                "date": getattr(note, 'date', 'Bilinmiyor'),
                "file_name": file_name,
                "file_size": file_size
            })
        return {"status": "success", "notes": notes_list}


def handle_create_request(data):
    username = data.get('username')
    title = data.get('title')
    content = data.get('content')

    if not username or not title or not content:
        return {"status": "error", "message": "Kullanıcı adı, başlık ve içerik gerekli"}

    with lock:
        global next_request_id
        now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        req = {
            "id": next_request_id,
            "title": title,
            "content": content,
            "author": username,
            "date": now_str,
            "comments": []
        }
        requests_data[next_request_id] = req
        next_request_id += 1
        save_requests()
        return {"status": "success", "message": "İstek oluşturuldu", "request_id": req["id"]}


def handle_delete_request(data):
    username = data.get('username')
    request_id = data.get('request_id')

    if not username or request_id is None:
        return {"status": "error", "message": "Parametreler eksik"}

    request_id = int(request_id)
    with lock:
        if request_id not in requests_data:
            return {"status": "error", "message": "İstek bulunamadı"}

        if str(requests_data[request_id]["author"]).strip() != str(username).strip():
            return {"status": "error", "message": "Bu isteği sonlandırma yetkiniz yok!"}

        del requests_data[request_id]
        save_requests()
        return {"status": "success", "message": "İstek sonlandırıldı"}


def handle_get_all_requests(data):
    with lock:
        req_list = list(requests_data.values())
        req_list.sort(key=lambda r: r["id"], reverse=True)
        return {"status": "success", "requests": req_list}


def handle_add_comment(data):
    username = data.get('username')
    request_id = data.get('request_id')
    comment = data.get('comment')

    if not username or request_id is None or not comment:
        return {"status": "error", "message": "Eksik parametre"}

    request_id = int(request_id)
    with lock:
        if request_id not in requests_data:
            return {"status": "error", "message": "İstek bulunamadı"}

        now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        comment_obj = {
            "author": username,
            "content": comment,
            "date": now_str
        }
        requests_data[request_id]["comments"].append(comment_obj)
        save_requests()
        return {"status": "success", "message": "Yorum eklendi", "comments": requests_data[request_id]["comments"]}


if __name__ == '__main__':
    load_data()
    print(f"🚀 SAÜ Connect Web Sunucusu Başlatılıyor: http://localhost:{PORT}")
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
