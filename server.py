import argparse
import socket
import json


class ChatServer:
    def __init__(self, PORT):
        self.BUFFER_SIZE = 65507
        self.UDP_IP = "127.0.0.1"
        """initialize the chatServer on the UDP port."""
        self.PORT = int(PORT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.PORT))
        self.users = {}
        self.receive_messages()

    def receive_messages(self):
        while True:
            data, address = self.sock.recvfrom(self.BUFFER_SIZE)  # buffer size is 65507 bytes
            parsed_data = json.loads(data)
            if parsed_data["command"] == "list":
                self.send_messages(json.dumps(self.users), address)
            if parsed_data["command"] == "signin":
                if self.users.get(parsed_data["username"]):
                    self.send_messages("User exists", address)
                else:
                    self.users[parsed_data["username"]] = address
                    self.send_messages("Success", address)
            if parsed_data["command"] == "send":
                self.send_messages(json.dumps(self.users.get(parsed_data["user"])), address)
            if parsed_data["command"] == "terminate":
                if self.users.get(parsed_data["username"]):
                    del self.users[parsed_data["username"]]

    def send_messages(self, message, ip):
        self.sock.sendto(message, ip)  


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-sp", "--sp")
    args = parser.parse_args()
    print("Server Initialized...")
    cs = ChatServer(args.sp)
