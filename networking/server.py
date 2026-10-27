import socket
import os
import threading
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from notes import note

# Configuration
HOST = '0.0.0.0'
PORT = 5000
ACCOUNTS_FILE = 'accounts.txt'
NOTES_FILE = 'notes.txt'
NEXT_ID_FILE = 'next_id.txt'  # Track the next available note ID

# Make sure files exist
if not os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, 'w') as f:
        f.write("")
if not os.path.exists(NOTES_FILE):
    with open(NOTES_FILE, 'w') as f:
        f.write("")
if not os.path.exists(NEXT_ID_FILE):
    with open(NEXT_ID_FILE, 'w') as f:
        f.write("1")

def get_next_id():
    """Get the next available note ID."""
    with open(NEXT_ID_FILE, 'r') as f:
        next_id = int(f.read().strip())
    return next_id

def increment_id():
    """Increment the next available ID."""
    next_id = get_next_id()
    with open(NEXT_ID_FILE, 'w') as f:
        f.write(str(next_id + 1))
    return next_id

def load_accounts():
    """Read all accounts from file into a dictionary."""
    accounts = {}
    with open(ACCOUNTS_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line and ':' in line:
                username, password = line.split(':', 1)
                accounts[username] = password
    return accounts

def load_notes():
    """Read all notes from file into a list."""
    notes = []
    with open(NOTES_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line and ':' in line:
                parts = line.split(':', 3)  # Split into max 4 parts
                if len(parts) >= 3:
                    note_id = int(parts[0])
                    title = parts[1]
                    content = parts[2]
                    likes = int(parts[3]) if len(parts) > 3 else 0
                    note_obj = note.Note(title, content, _id=note_id, likes=likes)
                    notes.append(note_obj)
    return notes

def get_note_by_id(note_id):
    """Retrieve a single note by its ID."""
    notes = load_notes()
    for note_obj in notes:
        if note_obj.id == note_id:
            return note_obj
    return None

def save_accounts(accounts):
    """Write all accounts to file."""
    with open(ACCOUNTS_FILE, 'w') as f:
        for username, password in accounts.items():
            f.write(f"{username}:{password}\n")

def save_notes(notes):
    """Write all notes to file."""
    with open(NOTES_FILE, 'w') as f:
        for note_obj in notes:
            f.write(f"{note_obj.id}:{note_obj.title}:{note_obj.content}:{note_obj.likes}\n")

def handle_client(client_socket, client_address):
    """Handle a single client connection."""
    print(f"[NEW CONNECTION] Client connected from {client_address}")

    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')

            if not data:
                break

            print(f"[RECEIVED] From {client_address}: {data}")

            parts = data.split(':', 2)
            command = parts[0]
            response = "ERROR:Unknown command"

            accounts = load_accounts()

            if command == "REGISTER":
                if len(parts) < 3:
                    response = "ERROR:Invalid format. Use REGISTER:username:password"
                else:
                    username = parts[1]
                    password = parts[2]

                    if username in accounts:
                        response = "ERROR:Username already exists"
                    else:
                        accounts[username] = password
                        save_accounts(accounts)
                        response = "SUCCESS:Account created!"

            elif command == "LOGIN":
                if len(parts) < 3:
                    response = "ERROR:Invalid format. Use LOGIN:username:password"
                else:
                    username = parts[1]
                    password = parts[2]

                    if username not in accounts:
                        response = "ERROR:Username not found"
                    elif accounts[username] != password:
                        response = "ERROR:Incorrect password"
                    else:
                        response = f"SUCCESS:Welcome {username}!"

            elif command == "CREATE_NOTE":
                if len(parts) < 3:
                    response = "ERROR:Invalid format. Use CREATE_NOTE:title:content"
                else:
                    title = parts[1]
                    content = parts[2]

                    # Get next ID and increment
                    note_id = increment_id()

                    # Create note with ID
                    notes = load_notes()
                    new_note = note.Note(title, content, _id=note_id, likes=0)
                    notes.append(new_note)
                    save_notes(notes)

                    response = f"SUCCESS:Note created with ID {note_id}!"

            elif command == "GET_NOTE":
                if len(parts) < 2:
                    response = "ERROR:Invalid format. Use GET_NOTE:id"
                else:
                    try:
                        note_id = int(parts[1])
                        found_note = get_note_by_id(note_id)

                        if found_note is None:
                            response = f"ERROR:Note with ID {note_id} not found"
                        else:
                            response = f"SUCCESS:ID={found_note.id}|Title={found_note.title}|Content={found_note.content}|Likes={found_note.likes}"
                    except ValueError:
                        response = "ERROR:ID must be a number"

            elif command == "GET_ALL_NOTES":
                notes = load_notes()
                if not notes:
                    response = "SUCCESS:No notes found"
                else:
                    notes_str = ";".join([f"ID={n.id}|Title={n.title}|Likes={n.likes}" for n in notes])
                    response = f"SUCCESS:{notes_str}"

            client_socket.send(response.encode('utf-8'))
            print(f"[SENT] To {client_address}: {response}")

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        client_socket.close()
        print(f"[DISCONNECTED] Client from {client_address} disconnected")

def start_server():
    """Main server loop."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"[STARTING] Server listening on {HOST}:{PORT}")
    print("Waiting for connections...\n")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address)
            )
            client_thread.daemon = True
            client_thread.start()

    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
