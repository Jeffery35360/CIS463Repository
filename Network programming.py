import socket
import threading
import os
import string
import random

def monoalphabetic_encrypt(plaintext, cipher_key=None, mode="encrypt"):
    alphabet = list(string.ascii_uppercase)
    
    if cipher_key is None:
        cipher_key = alphabet.copy()
        random.shuffle(cipher_key)
    
    # Map original alphabet to cipher key
    key = dict(zip(alphabet, cipher_key))
    print(f"key: {key}")  # randomly arranged alphabets
    
    result = ""
    if mode == "decrypt":
        reverse_key = {v: k for k, v in key.items()}  # Reverse the mapping
        for char in plaintext:
            if char.isalpha():
                if char.isupper():
                    result += reverse_key.get(char, char)
                else:
                    result += reverse_key.get(char.upper(), char).lower()
            else:
                result += char  # Keep non-alphabet characters unchanged
    else:
        for char in plaintext:
            if char.isalpha():
                if char.isupper():
                    result += key.get(char, char)
                else:
                    result += key.get(char.upper(), char).lower()
            else:
                result += char  # Keep non-alphabet characters unchanged

    return result

# Server setup
def server_mode(host='0.0.0.0', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    def receive_file(connection):
        file_name = connection.recv(1024).decode()
        file_size = connection.recv(1024).decode()

        with open(file_name, 'wb') as file:
            received = 0
            while received < int(file_size):
                data = connection.recv(1024)
                file.write(data)
                received += len(data)
        print(f"File {file_name} received successfully.")

    def receive_text(connection, cipher_key):
        text = connection.recv(1024).decode()
        print(f"Received encrypted text: {text}")
        
        decrypted_text = monoalphabetic_encrypt(text, cipher_key, mode="decrypt")
        print("Decrypted:", decrypted_text)

    while True:
        conn, addr = server_socket.accept()
        print(f"Connected to {addr}")

        # Generate cipher key and send it to client
        cipher_key = list(string.ascii_uppercase)
        random.shuffle(cipher_key)
        print(f"Server's Cipher Key: {cipher_key}")
        
        # Send cipher key to client
        conn.sendall(''.join(cipher_key).encode())

        data_type = conn.recv(1024).decode()  # 'text' or 'file'
        
        if data_type == 'text':
            receive_text(conn, cipher_key)
            
        elif data_type == 'file':
            receive_file(conn)

        conn.close()

# Client setup
def client_mode(server_ip, server_port=12345):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port)) 

    def send_text(text, cipher_key):
        client_socket.sendall(b'text')
        encrypted_text = monoalphabetic_encrypt(text, cipher_key, mode="encrypt")
        client_socket.sendall(encrypted_text.encode())
        print(f"Sent encrypted text: {encrypted_text}")
        
    def send_file(file_path):
        client_socket.sendall(b'file')
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        client_socket.sendall(file_name.encode())
        client_socket.sendall(str(file_size).encode())

        with open(file_path, 'rb') as file:
            while (data := file.read(1024)):
                client_socket.sendall(data)
        print(f"File {file_name} sent successfully.")

    # Receive the cipher key from the server
    cipher_key = client_socket.recv(1024).decode()
    cipher_key = list(cipher_key)
    print(f"Received Cipher Key: {cipher_key}")

    # Example usage
    option = input("Send text or file? (text/file): ").strip()

    if option == "text":
        text = input("Enter the text to send: ")
        send_text(text, cipher_key)

    elif option == "file":
        file_path = input("Enter the file path: ").strip()
        send_file(file_path)

    client_socket.close()

def start_bidirectional():
    mode = input("Run as server or client? (server/client): ").strip().lower()
    if mode == "server":
        server_mode()
    elif mode == "client":
        server_ip = input("Enter the server IP address: ").strip()
        client_mode(server_ip)
    else:
        print("Invalid mode. Please enter 'server' or 'client'.")
    
if __name__ == "__main__":
    threading.Thread(target=start_bidirectional).start()
