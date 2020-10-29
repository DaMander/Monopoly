from constants import  *
from _thread import *
import  _pickle as pickle
import socket
import pickle



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 5672       # Port to listen on (non-privileged ports are > 1023)

try:
    sock.bind((HOST, PORT))
except socket.error as e:
    print(str(e))
    print("Server did not start")
    quit()

sock.listen()

print(f"server started with IP-{HOST}")

#variables that change
players = {}
connections = 0
_id = 0
start = False

def threaded_client(conn, _id):

    global players, connections

    player_id = _id

    #get name from client
    data = conn.recv(16)
    name = data.decode("utf-8")
    print(f"{name} connected to the server")

    #setting up player
    colour = list(COLOURS.values())[player_id]
    players[player_id] = {"start_pos":0, "radius": 14 , "colour": colour,  "name": name }


    conn.send(str.encode(str(player_id)))

    while  True:
        try:
            #recieve from client
            data = conn.recv(32)

            if not data:
                break

            data = data.decode("utf-8")

            """This is where you recieve info from the clients and send it back
            """






        except Exception as e:
            print(e)
            break


    print(f"{name},({player_id}) disconnected")

    connections -= 1
    del players[player_id]
    conn.close()

print("Waiting for connections")

while True:

    host, addr = sock.accept()
    print(f"Connected to: {addr}")

    connections += 1
    start_new_thread(threaded_client,(host,_id))
    _id += 1
