import socket
import json
import threading
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../notes')))
from notes import note
from user import User
from user_profile import Profile


HOST = 'localhost'
PORT = 5000
DATA_DIR = 'data'

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# File paths
ACCOUNTS_FILE = os.path.join(DATA_DIR, 'accounts.txt')
NOTES_FILE = os.path.join(DATA_DIR, 'notes.txt')
NEXT_ID_FILE = os.path.join(DATA_DIR, 'next_id.txt')
LIKES_FILE = os.path.join(DATA_DIR, 'likes.txt')
PROFILES_FILE = os.path.join(DATA_DIR, 'user_profiles.txt')

# In-memory data structures
users = {}  # {username: User}
notes = {}  # {note_id: Note}
authenticated_users = {}  # {connection_id: username}
user_likes = {}  # {(username, note_id): True}
next_note_id = 1
lock = threading.Lock()

def load_data():
    """Load all persistent data from files."""
    global next_note_id, users, notes, user_likes

    # Load accounts
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r') as f:
            for line in f:
                user = User.from_string(line)
                if user:
                    users[user.username] = user

    # Load profiles
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, 'r') as f:
            for line in f:
                profile = Profile.from_string(line)
                if profile and profile.username in users:
                    users[profile.username].profile = profile

    # Load next ID
    if os.path.exists(NEXT_ID_FILE):
        with open(NEXT_ID_FILE, 'r') as f:
            try:
                next_note_id = int(f.read().strip())
            except ValueError:
                next_note_id = 1

    # Load notes
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, 'r') as f:
            for line in f:
                note = Note.from_string(line)
                if note:
                    notes[note.id] = note

    # Load likes
    if os.path.exists(LIKES_FILE):
        with open(LIKES_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2:
                    user_likes[(parts[0], int(parts[1]))] = True

def save_accounts():
    """Save user accounts to file."""
    with open(ACCOUNTS_FILE, 'w') as f:
        for user in users.values():
            f.write(user.to_string() + '\n')

def save_profiles():
    """Save user profiles to file."""
    with open(PROFILES_FILE, 'w') as f:
        for user in users.values():
            f.write(user.profile.to_string() + '\n')

def save_notes():
    """Save notes to file."""
    with open(NOTES_FILE, 'w') as f:
        for note in notes.values():
            f.write(note.to_string() + '\n')

def save_next_id():
    """Save the next note ID to file."""
    with open(NEXT_ID_FILE, 'w') as f:
        f.write(str(next_note_id))

def save_likes():
    """Save likes to file."""
    with open(LIKES_FILE, 'w') as f:
        for (username, note_id) in user_likes.keys():
            f.write(f"{username}|{note_id}\n")

def handle_register(data):
    """Handle REGISTER command."""
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {"status": "error", "message": "Username and password required"}

    with lock:
        if username in users:
            return {"status": "error", "message": "Username already exists"}

        user = User(username, password, Profile(username))
        users[username] = user
        save_accounts()
        save_profiles()
        return {"status": "success", "message": "Account created"}

def handle_login(data):
    """Handle LOGIN command."""
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {"status": "error", "message": "Username and password required"}

    with lock:
        if username not in users:
            return {"status": "error", "message": "User not found"}

        if users[username].password != password:
            return {"status": "error", "message": "Invalid password"}

        return {"status": "success", "message": "Login successful"}

def handle_logout(data):
    """Handle LOGOUT command."""
    username = data.get('username')

    if not username:
        return {"status": "error", "message": "Username required"}

    return {"status": "success", "message": "Logout successful"}

def handle_create_note(data):
    """Handle CREATE_NOTE command."""
    username = data.get('username')
    title = data.get('title')
    content = data.get('content')

    if not username or not title or not content:
        return {"status": "error", "message": "Username, title, and content required"}

    with lock:
        if username not in users:
            return {"status": "error", "message": "User not found"}

        global next_note_id
        note = Note(next_note_id, title, content, username)
        notes[next_note_id] = note
        users[username].profile.add_note(next_note_id)
        next_note_id += 1

        save_notes()
        save_next_id()
        save_profiles()

        return {"status": "success", "message": "Note created", "note_id": note.id}

def handle_get_note(data):
    """Handle GET_NOTE command."""
    note_id = data.get('note_id')

    if note_id is None:
        return {"status": "error", "message": "Note ID required"}

    note_id = int(note_id)

    with lock:
        if note_id not in notes:
            return {"status": "error", "message": "Note not found"}

        note = notes[note_id]
        return {
            "status": "success",
            "note": {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "author": note.author,
                "likes": note.likes
            }
        }

def handle_get_all_notes(data):
    """Handle GET_ALL_NOTES command."""
    with lock:
        notes_list = []
        for note in notes.values():
            notes_list.append({
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "author": note.author,
                "likes": note.likes
            })
        return {"status": "success", "notes": notes_list}

def handle_get_note_author(data):
    """Handle GET_NOTE_AUTHOR command."""
    note_id = data.get('note_id')

    if note_id is None:
        return {"status": "error", "message": "Note ID required"}

    note_id = int(note_id)

    with lock:
        if note_id not in notes:
            return {"status": "error", "message": "Note not found"}

        return {"status": "success", "author": notes[note_id].author}

def handle_get_user_notes(data):
    """Handle GET_USER_NOTES command."""
    username = data.get('username')

    if not username:
        return {"status": "error", "message": "Username required"}

    with lock:
        if username not in users:
            return {"status": "error", "message": "User not found"}

        note_ids = users[username].profile.note_ids
        return {"status": "success", "note_ids": note_ids}

def handle_like_note(data):
    """Handle LIKE_NOTE command."""
    username = data.get('username')
    note_id = data.get('note_id')

    if not username or note_id is None:
        return {"status": "error", "message": "Username and note ID required"}

    note_id = int(note_id)

    with lock:
        if username not in users:
            return {"status": "error", "message": "User not found"}

        if note_id not in notes:
            return {"status": "error", "message": "Note not found"}

        if (username, note_id) in user_likes:
            return {"status": "error", "message": "User has already liked this note"}

        notes[note_id].likes += 1
        user_likes[(username, note_id)] = True
        save_notes()
        save_likes()

        return {"status": "success", "message": "Note liked", "likes": notes[note_id].likes}

def handle_client(conn, addr):
    """Handle a client connection."""
    try:
        data = conn.recv(4096).decode('utf-8')
        if not data:
            return

        request = json.loads(data)
        command = request.get('command')

        if command == 'REGISTER':
            response = handle_register(request)
        elif command == 'LOGIN':
            response = handle_login(request)
        elif command == 'LOGOUT':
            response = handle_logout(request)
        elif command == 'CREATE_NOTE':
            response = handle_create_note(request)
        elif command == 'GET_NOTE':
            response = handle_get_note(request)
        elif command == 'GET_ALL_NOTES':
            response = handle_get_all_notes(request)
        elif command == 'GET_NOTE_AUTHOR':
            response = handle_get_note_author(request)
        elif command == 'GET_USER_NOTES':
            response = handle_get_user_notes(request)
        elif command == 'LIKE_NOTE':
            response = handle_like_note(request)
        else:
            response = {"status": "error", "message": "Unknown command"}

        conn.sendall(json.dumps(response).encode('utf-8'))
    except Exception as e:
        response = {"status": "error", "message": str(e)}
        conn.sendall(json.dumps(response).encode('utf-8'))
    finally:
        conn.close()

def start_server():
    """Start the server and listen for client connections."""
    load_data()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server started on {HOST}:{PORT}")

        try:
            while True:
                conn, addr = server_socket.accept()
                print(f"Connection from {addr}")
                thread = threading.Thread(target=handle_client, args=(conn, addr))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            server_socket.close()

if __name__ == '__main__':
    start_server()
