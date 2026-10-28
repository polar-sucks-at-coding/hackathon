import socket
import json

HOST = 'localhost'
PORT = 5000

def send_command(command_dict):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))
            message = json.dumps(command_dict)
            sock.sendall(message.encode('utf-8'))

            chunks = []
            while True:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                chunks.append(chunk)
            response_data = b"".join(chunks).decode('utf-8')
            return json.loads(response_data)
    except Exception as e:
        return {"status": "error", "message": str(e)}

def send_register(username, password, faculty="", department="", about="", profile_image=""):
    return send_command({
        "command": "REGISTER",
        "username": username,
        "password": password,
        "faculty": faculty,
        "department": department,
        "about": about,
        "profile_image": profile_image
    })

def send_login(username, password):
    return send_command({"command": "LOGIN", "username": username, "password": password})

def send_logout(username):
    return send_command({"command": "LOGOUT", "username": username})

def send_update_profile(username, faculty, department, about="", profile_image=""):
    return send_command({
        "command": "UPDATE_PROFILE",
        "username": username,
        "faculty": faculty,
        "department": department,
        "about": about,
        "profile_image": profile_image
    })

def send_create_note(username, title, content, file_name=None, file_data=None):
    return send_command({
        "command": "CREATE_NOTE",
        "username": username,
        "title": title,
        "content": content,
        "file_name": file_name,
        "file_data": file_data
    })

def send_get_note(note_id, username=None):
    return send_command({"command": "GET_NOTE", "note_id": note_id, "username": username})

def send_delete_note(username, note_id):
    return send_command({"command": "DELETE_NOTE", "username": username, "note_id": note_id})

def send_get_all_notes():
    return send_command({"command": "GET_ALL_NOTES"})

def send_like_note(username, note_id):
    return send_command({"command": "LIKE_NOTE", "username": username, "note_id": note_id})

def send_download_file(note_id):
    return send_command({"command": "DOWNLOAD_FILE", "note_id": note_id})

def send_create_request(username, title, content):
    return send_command({"command": "CREATE_REQUEST", "username": username, "title": title, "content": content})

def send_delete_request(username, request_id):
    return send_command({"command": "DELETE_REQUEST", "username": username, "request_id": request_id})

def send_get_all_requests():
    return send_command({"command": "GET_ALL_REQUESTS"})

def send_add_comment(username, request_id, comment):
    return send_command({"command": "ADD_COMMENT", "username": username, "request_id": request_id, "comment": comment})

def send_create_team(username, title, description, skills, current_members=1, target_members=5):
    return send_command({
        "command": "CREATE_TEAM",
        "username": username,
        "title": title,
        "description": description,
        "skills": skills,
        "current_members": current_members,
        "target_members": target_members
    })

def send_get_all_teams():
    return send_command({"command": "GET_ALL_TEAMS"})

def send_join_team(username, team_id):
    return send_command({"command": "JOIN_TEAM", "username": username, "team_id": team_id})

def send_leave_team(username, team_id):
    return send_command({"command": "LEAVE_TEAM", "username": username, "team_id": team_id})

def send_kick_member(username, team_id, target_username):
    return send_command({
        "command": "KICK_MEMBER",
        "username": username,
        "team_id": team_id,
        "target_username": target_username
    })

def send_delete_team(username, team_id):
    return send_command({"command": "DELETE_TEAM", "username": username, "team_id": team_id})

def send_get_all_users():
    return send_command({"command": "GET_ALL_USERS"})

def send_get_user_profile(target_username):
    return send_command({"command": "GET_USER_PROFILE", "target_username": target_username})
