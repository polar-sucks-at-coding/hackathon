import socket

# Configuration
HOST = '127.0.0.1'
PORT = 5000

def send_command(command):
    """Send a command to the server and return the response."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))

        client_socket.send(command.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')

        client_socket.close()
        return response

    except ConnectionRefusedError:
        return "ERROR:Could not connect to server. Is it running?"
    except Exception as e:
        return f"ERROR:{str(e)}"

# Frontend convenience functions
def send_register(username, password):
    """Register a new account."""
    return send_command(f"REGISTER:{username}:{password}")

def send_login(username, password):
    """Login to an account."""
    return send_command(f"LOGIN:{username}:{password}")

def send_logout():
    """Logout from the current account."""
    return send_command("LOGOUT")

def send_create_note(title, content):
    """Create a new note. Returns the note ID if successful."""
    response = send_command(f"CREATE_NOTE:{title}:{content}")
    # Response format: "SUCCESS:Note created with ID 1!"
    # Extract ID from response if successful
    if response.startswith("SUCCESS"):
        return response
    return response

def send_get_note(note_id):
    """Retrieve a note by its ID."""
    response = send_command(f"GET_NOTE:{note_id}")
    # Response format: "SUCCESS:ID=1|Title=...|Content=...|Likes=..."
    if response.startswith("SUCCESS"):
        # Parse the response into a dictionary
        data = response.replace("SUCCESS:", "").split("|")
        note_dict = {}
        for item in data:
            if "=" in item:
                key, value = item.split("=", 1)
                note_dict[key] = value
        return note_dict
    return response

def send_get_all_notes():
    """Retrieve all notes with their IDs and titles."""
    response = send_command("GET_ALL_NOTES")
    # Response format: "SUCCESS:ID=1|Title=...|Likes=...;ID=2|Title=...|Likes=..."
    if response.startswith("SUCCESS"):
        data = response.replace("SUCCESS:", "")
        if data == "No notes found":
            return []
        notes_list = []
        for note_str in data.split(";"):
            note_dict = {}
            for item in note_str.split("|"):
                if "=" in item:
                    key, value = item.split("=", 1)
                    note_dict[key] = value
            if note_dict:
                notes_list.append(note_dict)
        return notes_list
    return response

def send_like_note(note_id):
    """
    Add a like to a note by its ID.
    User must be logged in first.
    Response format: "SUCCESS:Note {id} liked! Total likes: {count}"
    or "ERROR:You must be logged in to like notes..."
    or "ERROR:You have already liked note {id}"
    """
    response = send_command(f"LIKE_NOTE:{note_id}")
    return response
