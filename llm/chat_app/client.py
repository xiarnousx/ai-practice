import socket
import threading

def main():
    host = 'localhost'
    port = 5000

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")

        def send_messages():
            while True:
                message = input("Enter message to send: ")
                client_socket.sendall(message.encode())

        def receive_messages():
            while True:
                data = client_socket.recv(1024)
                if not data:
                    print("Server closed the connection.")
                    break
                print(f"Received from server: {data.decode()}")

        sender_thread = threading.Thread(target=send_messages, daemon=True)
        receiver_thread = threading.Thread(target=receive_messages, daemon=True)

        sender_thread.start()
        receiver_thread.start()

        sender_thread.join()
        receiver_thread.join()

if __name__ == "__main__":
    main()