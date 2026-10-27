import socket

# Configuration
HOST = '127.0.0.1'  # IP address of the server (localhost = your own computer)
PORT = 5000         # Must match the server's port

def send_command(command):
    try:
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        client_socket.connect((HOST, PORT))
        print(f"[CONNECTED] Connected to server at {HOST}:{PORT}\n")

        # Send the command
        client_socket.send(command.encode('utf-8'))
        print(f"[SENT] {command}")

        # Receive the response
        response = client_socket.recv(1024).decode('utf-8')
        print(f"[RESPONSE] {response}\n")

        # Close the connection
        client_socket.close()
        return response

    except ConnectionRefusedError:
        print("[ERROR] Could not connect to server. Is it running?\n")
    except Exception as e:
        print(f"[ERROR] {e}\n")
