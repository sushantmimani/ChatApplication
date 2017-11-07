Program Description: The program creates a simple chat application using socket programming in Python. The server listens to incoming requests from clients, on a specified port and performs actions based on the commands that it receives from the client. The client program, on startup, registers a user with the server and then permits the user to send commands to the server and send messages to other clients

Requirements:
The programs have been written on Python 3.5.1 and require libraries argparse, socket, json, sys and select

Steps:
To start server:
python server.py -sp <port>

To start client
python client.py -u <username> -sip <server_ip (127.0.0.1)> -sp <server_port (same as port used to start the server)>