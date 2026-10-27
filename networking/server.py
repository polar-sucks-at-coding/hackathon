import socket
import os
import threading

# Configuration
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 5000        # The port to listen on
ACCOUNTS_FILE = 'accounts.txt'  # File where we store usernames & passwords

# Make sure accounts file exists
if not os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, 'w') as f:
        f.write("")  # Create empty file

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

def save_accounts(accounts):
    """Write all accounts to file."""
    with open(ACCOUNTS_FILE, 'w') as f:
        for username, password in accounts.items():
            f.write(f"{username}:{password}\n")

def handle_client(client_socket, client_address):
    """
    Handle a single client connection.
    This runs in a separate thread for each client.
    """
    print(f"[NEW CONNECTION] Client connected from {client_address}")

    try:
        while True:
            # Receive data from client (up to 1024 bytes)
            data = client_socket.recv(1024).decode('utf-8')

            if not data:
                # Client disconnected
                break

            print(f"[RECEIVED] From {client_address}: {data}")

            # Parse the command
            parts = data.split(':')
            command = parts[0]

            # Load current accounts
            accounts = load_accounts()

            # REGISTER command: "REGISTER:username:password"
            if command == "REGISTER":
                username = parts[1]
                password = parts[2]

                if username in accounts:
                    response = "ERROR:Username already exists"
                else:
                    accounts[username] = password
                    save_accounts(accounts)
                    response = "SUCCESS:Account created!"

            # LOGIN command: "LOGIN:username:password"
            elif command == "LOGIN":
                username = parts[1]
                password = parts[2]

                if username not in accounts:
                    response = "ERROR:Username not found"
                elif accounts[username] != password:
                    response = "ERROR:Incorrect password"
                else:
                    response = f"SUCCESS:Welcome {username}!"

            else:
                response = "ERROR:Unknown command"

            # Send response back to client
            client_socket.send(response.encode('utf-8'))
            print(f"[SENT] To {client_address}: {response}")

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        client_socket.close()
        print(f"[DISCONNECTED] Client from {client_address} disconnected")

def start_server():
    """Main server loop."""
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind to the host and port
    server_socket.bind((HOST, PORT))

    # Listen for incoming connections (queue up to 5 clients)
    server_socket.listen(5)

    print(f"[STARTING] Server listening on {HOST}:{PORT}")
    print("Waiting for connections...\n")

    try:
        while True:
            # Accept a new client connection
            client_socket, client_address = server_socket.accept()

            # Create a new thread to handle this client
            # This way we can handle multiple clients at once
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address)
            )
            client_thread.daemon = True  # Thread dies if main program exits
            client_thread.start()

    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
