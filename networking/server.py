import os
import sys
import json
import threading
import datetime
import base64
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'notes'))

from notes.note import Note
from user import User
from user_profile import Profile

app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')
CORS(app)

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
TEAMS_FILE = os.path.join(DATA_DIR, 'teams.json')
REPORTS_FILE = os.path.join(DATA_DIR, 'reports.json')

users = {}
notes = {}
user_likes = {}
requests_data = {}
teams_data = {}
reports_data = []
next_note_id = 1
next_request_id = 1
next_team_id = 1
next_report_id = 1
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
    global next_note_id, next_request_id, next_team_id, next_report_id, users, notes, user_likes, requests_data, teams_data, reports_data

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

    if os.path.exists(TEAMS_FILE):
        try:
            with open(TEAMS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                teams_data = {int(k): v for k, v in data.get("teams", {}).items()}
                for t in teams_data.values():
                    t.setdefault("join_requests", [])
                    t.setdefault("messages", [])
                next_team_id = data.get("next_id", 1)
        except Exception as e:
            print(f"[LOAD TEAMS ERROR] {e}")

    if os.path.exists(REPORTS_FILE):
        try:
            with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                reports_data = data.get("reports", [])
                next_report_id = data.get("next_id", 1)
        except Exception as e:
            print(f"[LOAD REPORTS ERROR] {e}")


def save_accounts():
    with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
        for user in users.values():
            f.write(user.to_string() + '\n')


def save_profiles():
    with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
        for user in users.values():
            if user.profile:
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


def save_teams():
    try:
        with open(TEAMS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"teams": teams_data, "next_id": next_team_id}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[SAVE TEAMS ERROR] {e}")


def save_reports():
    try:
        with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"reports": reports_data, "next_id": next_report_id}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[SAVE REPORTS ERROR] {e}")


@app.route('/')
def index():
    index_path = os.path.join(BASE_DIR, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    return "index.html bulunamadı", 404


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
    elif command == 'UPDATE_PROFILE':
        return jsonify(handle_update_profile(request_data))
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
    elif command == 'CREATE_TEAM':
        return jsonify(handle_create_team(request_data))
    elif command == 'GET_ALL_TEAMS':
        return jsonify(handle_get_all_teams(request_data))
    elif command == 'JOIN_TEAM':
        return jsonify(handle_join_team(request_data))
    elif command == 'ACCEPT_JOIN_REQUEST':
        return jsonify(handle_accept_join_request(request_data))
    elif command == 'REJECT_JOIN_REQUEST':
        return jsonify(handle_reject_join_request(request_data))
    elif command == 'LEAVE_TEAM':
        return jsonify(handle_leave_team(request_data))
    elif command == 'KICK_MEMBER':
        return jsonify(handle_kick_member(request_data))
    elif command == 'DELETE_TEAM':
        return jsonify(handle_delete_team(request_data))
    elif command == 'ADD_TEAM_MESSAGE':
        return jsonify(handle_add_team_message(request_data))
    elif command == 'CREATE_REPORT':
        return jsonify(handle_create_report(request_data))
    elif command == 'GET_ALL_USERS':
        return jsonify(handle_get_all_users(request_data))
    elif command == 'GET_USER_PROFILE':
        return jsonify(handle_get_user_profile(request_data))
    else:
        return jsonify({"status": "error", "message": "Bilinmeyen komut"})


def handle_register(data):
    username = data.get('username')
    password = data.get('password')
    faculty = data.get('faculty', '').strip()
    department = data.get('department', '').strip()
    about = data.get('about', '').strip()
    profile_image = data.get('profile_image', '').strip()

    if not username or not password or not faculty or not department:
        return {"status": "error", "message": "Kullanıcı adı, şifre, fakülte ve bölüm alanları zorunludur!"}

    with lock:
        if username in users:
            return {"status": "error", "message": "Bu kullanıcı adı zaten alınmış"}

        user_profile = Profile(username, faculty, department, about, profile_image=profile_image)
        user = User(username, password, user_profile)
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

        user = users[username]
        f = user.profile.faculty if user.profile else ""
        d = user.profile.department if user.profile else ""
        a = user.profile.about if user.profile else ""
        img = user.profile.profile_image if user.profile else ""

        return {
            "status": "success",
            "message": "Giriş başarılı",
            "user": {
                "username": username,
                "faculty": f,
                "department": d,
                "about": a,
                "profile_image": img
            }
        }


def handle_logout(data):
    return {"status": "success", "message": "Çıkış yapıldı"}


def handle_update_profile(data):
    username = data.get('username')
    faculty = data.get('faculty', '').strip()
    department = data.get('department', '').strip()
    about = data.get('about', '').strip()
    profile_image = data.get('profile_image', '').strip()

    if not username or not faculty or not department:
        return {"status": "error", "message": "Fakülte ve bölüm alanları zorunludur!"}

    with lock:
        if username not in users:
            return {"status": "error", "message": "Kullanıcı bulunamadı"}

        user = users[username]
        if not user.profile:
            user.profile = Profile(username)

        user.profile.faculty = faculty
        user.profile.department = department
        user.profile.about = about
        if profile_image:
            user.profile.profile_image = profile_image

        save_profiles()
        return {
            "status": "success",
            "message": "Profil başarıyla güncellendi",
            "profile_image": user.profile.profile_image
        }


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
                # Gelen veride Data URL başlığı varsa temizle
                if ',' in file_b64:
                    file_b64 = file_b64.split(',', 1)[1]

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
        comment_id = len(requests_data[request_id]["comments"]) + 1
        comment_obj = {
            "id": comment_id,
            "author": username,
            "content": comment,
            "date": now_str
        }
        requests_data[request_id]["comments"].append(comment_obj)
        save_requests()
        return {"status": "success", "message": "Yorum eklendi", "comments": requests_data[request_id]["comments"]}


def handle_create_team(data):
    username = data.get('username')
    title = data.get('title')
    description = data.get('description')
    skills = data.get('skills', '')
    try:
        current_members = int(data.get('current_members', 1))
    except (ValueError, TypeError):
        current_members = 1

    try:
        target_members = int(data.get('target_members', 5))
    except (ValueError, TypeError):
        target_members = 5

    if not username or not title or not description or not skills:
        return {"status": "error", "message": "Başlık, açıklama ve gerekli yetenekler alanları gereklidir!"}

    if current_members > target_members:
        return {"status": "error", "message": "Mevcut üye sayısı hedef üye sayısından fazla olamaz!"}

    with lock:
        global next_team_id
        now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        team = {
            "id": next_team_id,
            "title": title,
            "description": description,
            "skills": skills,
            "author": username,
            "current_members": current_members,
            "target_members": target_members,
            "date": now_str,
            "members": [username],
            "join_requests": [],
            "messages": []
        }
        teams_data[next_team_id] = team
        next_team_id += 1
        save_teams()
        return {"status": "success", "message": "Takım ilanı başarıyla yayınlandı", "team_id": team["id"]}


def handle_get_all_teams(data):
    with lock:
        t_list = list(teams_data.values())
        for t in t_list:
            t.setdefault("join_requests", [])
            t.setdefault("messages", [])
        t_list.sort(key=lambda x: x["id"], reverse=True)
        return {"status": "success", "teams": t_list}


def handle_join_team(data):
    username = data.get('username')
    team_id = data.get('team_id')
    message = data.get('message', '').strip()

    if not username or team_id is None:
        return {"status": "error", "message": "Parametreler eksik"}

    if not message:
        return {"status": "error", "message": "Lütfen katılma isteği gönderirken kendinizden ve yeteneklerinizden bahsedin!"}

    team_id = int(team_id)
    with lock:
        if team_id not in teams_data:
            return {"status": "error", "message": "Takım ilanı bulunamadı"}

        team = teams_data[team_id]
        team.setdefault("join_requests", [])

        if username in team["members"]:
            return {"status": "error", "message": "Zaten bu takımın üyesiniz."}

        req_usernames = [r if isinstance(r, str) else r.get("username") for r in team["join_requests"]]
        if username in req_usernames:
            return {"status": "error", "message": "Zaten bu takıma katılım isteği gönderdiniz."}

        if team["current_members"] >= team["target_members"]:
            return {"status": "error", "message": "Takım kontenjanı dolu!"}

        now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        req_obj = {
            "username": username,
            "message": message,
            "date": now_str
        }
        team["join_requests"].append(req_obj)
        save_teams()
        return {"status": "success", "message": "Katılma isteği takım sahibine iletildi."}


def handle_accept_join_request(data):
    username = data.get('username')
    team_id = data.get('team_id')
    target_username = data.get('target_username')

    if not username or team_id is None or not target_username:
        return {"status": "error", "message": "Parametreler eksik"}

    team_id = int(team_id)
    with lock:
        if team_id not in teams_data:
            return {"status": "error", "message": "Takım ilanı bulunamadı"}

        team = teams_data[team_id]
        team.setdefault("join_requests", [])

        if str(team["author"]).strip() != str(username).strip():
            return {"status": "error", "message": "Sadece takım sahibi katılma isteklerini kabul edebilir!"}

        req_usernames = [r if isinstance(r, str) else r.get("username") for r in team["join_requests"]]
        if target_username not in req_usernames:
            return {"status": "error", "message": "Bu kullanıcının aktif bir katılma isteği bulunmuyor."}

        if team["current_members"] >= team["target_members"]:
            return {"status": "error", "message": "Takım kontenjanı dolu! Daha fazla üye kabul edilemez."}

        team["join_requests"] = [r for r in team["join_requests"] if (r if isinstance(r, str) else r.get("username")) != target_username]
        if target_username not in team["members"]:
            team["members"].append(target_username)
        team["current_members"] = len(team["members"])
        save_teams()
        return {"status": "success", "message": "Katılma isteği kabul edildi.", "current_members": team["current_members"]}


def handle_reject_join_request(data):
    username = data.get('username')
    team_id = data.get('team_id')
    target_username = data.get('target_username')

    if not username or team_id is None or not target_username:
        return {"status": "error", "message": "Parametreler eksik"}

    team_id = int(team_id)
    with lock:
        if team_id not in teams_data:
            return {"status": "error", "message": "Takım ilanı bulunamadı"}

        team = teams_data[team_id]
        team.setdefault("join_requests", [])

        if str(team["author"]).strip() != str(username).strip() and str(target_username).strip() != str(username).strip():
            return {"status": "error", "message": "Bu işlemi yapma yetkiniz yok!"}

        team["join_requests"] = [r for r in team["join_requests"] if (r if isinstance(r, str) else r.get("username")) != target_username]

        save_teams()
        return {"status": "success", "message": "Katılma isteği kaldırıldı."}


def handle_leave_team(data):
    username = data.get('username')
    team_id = data.get('team_id')

    if not username or team_id is None:
        return {"status": "error", "message": "Parametreler eksik"}

    team_id = int(team_id)
    with lock:
        if team_id not in teams_data:
            return {"status": "error", "message": "Takım ilanı bulunamadı"}

        team = teams_data[team_id]
        if username not in team["members"]:
            return {"status": "error", "message": "Bu takımın üyesi değilsiniz"}

        if username == team["author"]:
            return {"status": "error", "message": "Takım kurucusu ayrılamaz. İlanı silmeniz gerekmektedir."}

        team["members"].remove(username)
        team["current_members"] = len(team["members"])
        save_teams()
        return {"status": "success", "message": "Takımdan ayrıldınız.", "current_members": team["current_members"]}


def handle_kick_member(data):
    username = data.get('username')
    team_id = data.get('team_id')
    target_username = data.get('target_username')

    if not username or team_id is None or not target_username:
        return {"status": "error", "message": "Parametreler eksik"}

    team_id = int(team_id)
    with lock:
        if team_id not in teams_data:
            return {"status": "error", "message": "Takım ilanı bulunamadı"}

        team = teams_data[team_id]
        if str(team["author"]).strip() != str(username).strip():
            return {"status": "error", "message": "Sadece takım kurucusu üye çıkarabilir!"}

        if target_username == team["author"]:
            return {"status": "error", "message": "Takım kurucusu çıkarılamaz!"}

        if target_username not in team["members"]:
            return {"status": "error", "message": "Bu kullanıcı takım üyesi değil"}

        team["members"].remove(target_username)
        team["current_members"] = len(team["members"])
        save_teams()
        return {
            "status": "success",
            "message": f"@{target_username} takımdan çıkarıldı.",
            "current_members": team["current_members"],
            "members": team["members"]
        }


def handle_delete_team(data):
    username = data.get('username')
    team_id = data.get('team_id')

    if not username or team_id is None:
        return {"status": "error", "message": "Parametreler eksik"}

    team_id = int(team_id)
    with lock:
        if team_id not in teams_data:
            return {"status": "error", "message": "Takım ilanı bulunamadı"}

        if str(teams_data[team_id]["author"]).strip() != str(username).strip():
            return {"status": "error", "message": "Bu ilanı silme yetkiniz yok!"}

        del teams_data[team_id]
        save_teams()
        return {"status": "success", "message": "Takım ilanı silindi"}


def handle_add_team_message(data):
    username = data.get('username')
    team_id = data.get('team_id')
    content = data.get('content', '').strip()

    if not username or team_id is None or not content:
        return {"status": "error", "message": "Parametreler eksik veya mesaj boş!"}

    team_id = int(team_id)
    with lock:
        if team_id not in teams_data:
            return {"status": "error", "message": "Takım bulunamadı."}

        team = teams_data[team_id]
        if username not in team.get("members", []):
            return {"status": "error", "message": "Sadece takım üyeleri takıma mesaj gönderebilir!"}

        team.setdefault("messages", [])
        msg_id = len(team["messages"]) + 1
        now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        msg_obj = {
            "id": msg_id,
            "author": username,
            "content": content,
            "date": now_str
        }
        team["messages"].append(msg_obj)
        save_teams()
        return {"status": "success", "message": "Mesaj gönderildi", "messages": team["messages"]}


def handle_create_report(data):
    username = data.get('username')
    item_type = data.get('item_type')
    item_id = data.get('item_id')
    reason = data.get('reason', '').strip()

    if not username or not item_type or item_id is None or not reason:
        return {"status": "error", "message": "Tüm rapor alanları doldurulmalıdır."}

    with lock:
        global next_report_id
        now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        report = {
            "id": next_report_id,
            "reporter": username,
            "item_type": item_type,
            "item_id": item_id,
            "reason": reason,
            "date": now_str
        }
        reports_data.append(report)
        next_report_id += 1
        save_reports()
        return {"status": "success", "message": "Rapor başarıyla iletildi."}


def handle_get_all_users(data):
    with lock:
        all_usernames = set(users.keys())
        for n in notes.values():
            if n.author:
                all_usernames.add(n.author)
        for r in requests_data.values():
            if r.get("author"):
                all_usernames.add(r.get("author"))
        for t in teams_data.values():
            if t.get("author"):
                all_usernames.add(t.get("author"))

        user_list = []
        for username in all_usernames:
            user_notes = [n for n in notes.values() if str(n.author).strip() == str(username).strip()]
            total_likes = sum(n.likes for n in user_notes)
            user_reqs = [r for r in requests_data.values() if str(r.get("author")).strip() == str(username).strip()]
            user_teams = [t for t in teams_data.values() if str(t.get("author")).strip() == str(username).strip()]

            faculty = ""
            department = ""
            about = ""
            profile_image = ""
            if username in users and users[username].profile:
                p = users[username].profile
                faculty = p.faculty
                department = p.department
                about = p.about
                profile_image = getattr(p, 'profile_image', '')

            user_list.append({
                "username": username,
                "faculty": faculty,
                "department": department,
                "about": about,
                "profile_image": profile_image,
                "total_notes": len(user_notes),
                "total_likes": total_likes,
                "total_requests": len(user_reqs),
                "total_teams": len(user_teams)
            })
        return {"status": "success", "users": user_list}


def handle_get_user_profile(data):
    target_username = data.get('target_username')
    if not target_username:
        return {"status": "error", "message": "Kullanıcı adı gerekli"}

    with lock:
        faculty = ""
        department = ""
        about = ""
        profile_image = ""

        if target_username in users and users[target_username].profile:
            p = users[target_username].profile
            faculty = p.faculty
            department = p.department
            about = p.about
            profile_image = getattr(p, 'profile_image', '')

        user_notes = [n for n in notes.values() if str(n.author).strip() == str(target_username).strip()]
        user_reqs = [r for r in requests_data.values() if str(r.get("author")).strip() == str(target_username).strip()]
        user_teams = [t for t in teams_data.values() if str(t.get("author")).strip() == str(target_username).strip()]

        formatted_notes = []
        for note in user_notes:
            file_name = getattr(note, 'file_name', '')
            file_size = ""
            if file_name:
                file_path = os.path.join(UPLOADS_DIR, f"{note.id}_{file_name}")
                file_size = get_formatted_file_size(file_path)

            formatted_notes.append({
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "author": note.author,
                "likes": note.likes,
                "date": getattr(note, 'date', 'Bilinmiyor'),
                "file_name": file_name,
                "file_size": file_size
            })

        total_likes = sum(n["likes"] for n in formatted_notes)

        return {
            "status": "success",
            "profile": {
                "username": target_username,
                "faculty": faculty,
                "department": department,
                "about": about,
                "profile_image": profile_image,
                "total_notes": len(formatted_notes),
                "total_likes": total_likes,
                "total_requests": len(user_reqs),
                "total_teams": len(user_teams),
                "notes": formatted_notes,
                "requests": user_reqs,
                "teams": user_teams
            }
        }


if __name__ == '__main__':
    load_data()
    print(f"🚀 SAÜ Connect Sunucusu Çalışıyor: http://localhost:{PORT}")
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
