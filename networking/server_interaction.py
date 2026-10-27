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

def send_create_note(title, content):
    """Create a new note."""
    return send_command(f"CREATE_NOTE:{title}:{content}")

def send_get_note(note_id):
    """Retrieve a note by its ID."""
    return send_command(f"GET_NOTE:{note_id}")

def send_get_all_notes():
    """Retrieve all notes."""
    return send_command("GET_ALL_NOTES")
