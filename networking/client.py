import socket

# Configuration
HOST = '127.0.0.1'  # IP address of the server (localhost = your own computer)
PORT = 5000         # Must match the server's port

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
