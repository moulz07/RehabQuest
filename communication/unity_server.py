import socket
import json

HOST = "127.0.0.1"
PORT = 5005

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print("Waiting for Unity to connect...")

connection, address = server.accept()

print("Unity connected:", address)

while True:
    data = {
        "x": 0.5,
        "y": 0.5
    }

    message = json.dumps(data) + "\n"

    connection.sendall(message.encode("utf-8"))

    break

connection.close()
server.close()

print("Server closed.")