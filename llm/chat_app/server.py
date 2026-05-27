import socket
import threading

HOST = '0.0.0.0'
PORT = 5000

clients = []

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    clients.append(conn)
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Received from {addr}: {data.decode()}")
            conn.sendall(data)  # Echo back
            for client in clients:
                if client != conn:
                    try:
                        client.sendall(data)
                    except Exception:
                        pass
    finally:
        print(f"Connection closed: {addr}")
        clients.remove(conn)
        conn.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()

if __name__ == "__main__":
    main()