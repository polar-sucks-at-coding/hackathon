import socket
import json

HOST = 'localhost'
PORT = 5000

def send_command(command_dict):
    """Send a command to the server and receive the response."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))
            message = json.dumps(command_dict)
            sock.sendall(message.encode('utf-8'))
            response = sock.recv(4096).decode('utf-8')
            return json.loads(response)
    except Exception as e:
        return {"status": "error", "message": str(e)}

def send_register(username, password):
    return send_command({"command": "REGISTER", "username": username, "password": password})

def send_login(username, password):
    return send_command({"command": "LOGIN", "username": username, "password": password})

def send_logout(username):
    return send_command({"command": "LOGOUT", "username": username})

def send_create_note(username, title, content):
    return send_command({"command": "CREATE_NOTE", "username": username, "title": title, "content": content})

def send_get_note(note_id):
    return send_command({"command": "GET_NOTE", "note_id": note_id})

def send_get_all_notes():
    return send_command({"command": "GET_ALL_NOTES"})

def send_get_note_author(note_id):
    return send_command({"command": "GET_NOTE_AUTHOR", "note_id": note_id})

def send_get_user_notes(username):
    return send_command({"command": "GET_USER_NOTES", "username": username})

def send_like_note(username, note_id):
    return send_command({"command": "LIKE_NOTE", "username": username, "note_id": note_id})
