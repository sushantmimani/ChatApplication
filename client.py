import argparse
import socket
import json
import sys
from select import select


class ChatClient:
    def __init__(self, args):
        # Set the variables to be used in the rest of the program
        self.BUFFER_SIZE = 65507
        self.permitted_size = self.BUFFER_SIZE-32
        self.username = args.username
        self.UDP_IP = "127.0.0.1"
        self.sIP = args.sIP
        self.UDP_PORT = int(args.sp)
        # Initialize a socket for the client
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind socket to a random available port determined by the system
        self.sock.bind((self.UDP_IP, 0))
        # Parameters to allow server to register a user on sign-in
        params = {
            "command": "signin",
            "username": self.username
        }
        self.sock.sendto(json.dumps(params), (self.sIP, self.UDP_PORT))
        data, address = self.sock.recvfrom(self.BUFFER_SIZE)
        # Check if new user. Allow further processing only if user is a new user
        if data == "User exists":
            print("User exists! Try again!")
            exit()
        else:
            print("Client Started...")
            self.start()

    # Display messages received from other signed-in users
    def printreceivedmessage(self):
        data, address = self.sock.recvfrom(self.BUFFER_SIZE)  # buffer size is 65507 bytes
        print("<-- <From {0}:{1}:{2}>  " + json.loads(data)["message"]).format(address[0],
                                                                               address[1],
                                                                               json.loads(data)["user"])

    def printuserlist(self, input_array):
        if len(input_array) > 1:  # List followed by anything is an invalid command and will not be processed
            print("Invalid Input!")
        else:
            self.sock.sendto(json.dumps({"command": "list"}), (self.sIP, self.UDP_PORT))
            data, address = self.sock.recvfrom(self.BUFFER_SIZE)  # buffer size is 65507 bytes
            user = []
            parsed_user = json.loads(data)
            del parsed_user[args.username] # Delete current user from list of users returned from the server
            if not parsed_user: # No other users logged in
                print("<-- No other users signed in")
            else:
                for x in parsed_user:
                    user.append(x)
                print("<-- Signed In Users: {0}").format(','.join(user)) # Print user list

    # This function handles the overall working of the client
    def start(self):
        try:
            inp = [sys.stdin, self.sock]
            while 1:
                print('--> Enter command:')
                input_list, output_list, exception_list = select(inp, [], [])
                for s in input_list:
                    if s == self.sock:
                        self.printreceivedmessage()
                    elif s == sys.stdin:
                        input = raw_input()
                        input_array = input.split(" ")
                        # Perform different actions based on the command
                        if input_array[0] == "list":
                            self.printuserlist(input_array)
                        elif input_array[0] == "send":
                            if len(input_array)<3:
                                print("Invalid Input!")
                            else:
                                self.sock.sendto(json.dumps({"command": "send", "user":input_array[1]}),
                                                 (self.sIP, self.UDP_PORT))
                                data, address = self.sock.recvfrom(self.BUFFER_SIZE)  # buffer size is 65507 bytes
                                if data=="null":
                                    print("User doesn't exist!")
                                else:
                                    temp = json.loads(data)
                                    message = ' '.join(input_array[2:])
                                    if len(message.encode('utf-8')) > self.permitted_size:
                                        while len(message.encode('utf-8'))>self.permitted_size:
                                            toSend=message[0:self.permitted_size]
                                            self.sock.sendto(json.dumps({
                                                "user": self.username, "message": toSend}),
                                                (temp[0], int(temp[1])))
                                            message = message[self.permitted_size:]
                                        self.sock.sendto(json.dumps({
                                            "user": self.username, "message": message}),
                                            (temp[0], int(temp[1])))
                                    else:
                                        self.sock.sendto(json.dumps({
                                            "user":self.username,"message":' '.join(input_array[2:])}),
                                            (temp[0], int(temp[1])))
                        else:
                            print("Invalid Input!")
        except KeyboardInterrupt:
            self.sock.sendto(json.dumps({"command": "terminate", "username": self.username}), (self.sIP, self.UDP_PORT))
            self.sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username")
    parser.add_argument("-sip", "--sIP")
    parser.add_argument("-sp", "--sp")
    args = parser.parse_args()
    cs = ChatClient(args)
