from constants import  *
from _thread import *
from board import Board
import  _pickle as pickle
import socket
from game_rules import *




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
board = Board(WINDOW_WIDTH, WINDOW_HEIGHT)


def threaded_client(conn, _id):

    global players, connections, start, action_taken, triple_checker, jail_list, double, turn, have_enough_money, other_card

    player_id = _id

    #get name from client
    data = conn.recv(16)
    name = data.decode("utf-8")
    print(f"{name} connected to the server")

    #setting up player
    colour = list(COLOURS.values())[player_id]
    print(player_id)
    players[player_id] = Player(0,14 ,colour,starting_money,name,[] )


    conn.send(str.encode(str(player_id)))

    while  True:
        try:
            pl_list = []
            for i in list(players):
                pl_list.append(players[i])

            #recieve from client
            data = conn.recv(32)

            if not data:
                break

            data = data.decode("utf-8")

            """This is where you recieve info from the clients and send it back
            """

            if data == "ROLL DICE":
                roll = dice_roll()
                if roll[1]:
                    triple_checker += 1
                    double = True
                if pl_list[turn] not in jail_list or double == True:
                    if not check_for_triple(triple_checker):
                        pl_list[turn].move(roll[0])  # when the player clicks roll dice it gets the number and then using the property_action function determines what property has been landed on
                        action_taken = pl_list[turn].property_action(board)
                    else:
                        pl_list[turn].to_jail()
                        jail_list.append(pl_list[turn])
                        double = False
                        action_taken = 1
                else:
                    action_taken = 1
                    jail_list.remove(pl_list[turn])

            elif data == "END TURN" and have_enough_money == True:
                if double != True:
                    turn += 1
                    turn %= len(pl_list)
                    triple_checker = 0
                other_card = None
                double = False
                deal_player = None
                action_taken = 0  # this will reset it and then let the next player have their turn

            elif data == "LOOK AT PROPERTIES":
                action_taken = 11

            elif data == "PURCHASE":
                if pl_list[turn].buy_property(board):
                    action_taken = 1

            elif data == "BACK":
                if action_taken == 5:
                    action_taken = 11
                else:
                    action_taken = 1
                    other_card = None

            elif data == "+ HOUSE":
                pl_list[turn].add_house(board, other_card)

            elif data == "- HOUSE":
                pl_list[turn].remove_house(board, other_card)

            elif data == "MORTGAGE":
                pl_list[turn].mortgage(board, other_card)

            elif data == "UNMORTGAGE":
                pl_list[turn].unmortgage(board, other_card)

            elif data == "FINISHED":
                action_taken = 4

            elif data == "BANK":
                # function that takes in have_enough_money variable to decide whether another player takes there propertys else it goes to the bank and free parking
                pl_list[turn].remove_assets(board, have_enough_money)
                pl_list.remove(pl_list[turn])
                turn %= len(pl_list)
                triple_checker = 0
                other_card = None
                double = False
                deal_player = None
                action_taken = 0
                have_enough_money = True

            send_board = board.convert_for_send(pl_list)

            pl_dict = {}
            for i in list(players):
                pl_index = []
                for set in players[i].owned_propertys:
                    for prop in set:
                        pl_index.append(board.properties.index(prop))
                pl_dict[i] = list(players[i].return_variables())
                pl_dict[i][-1] = pl_index






            data_send = pickle.dumps((send_board,action_taken, pl_dict, turn, other_card, None, None))


            conn.send(data_send)




        except Exception as e:
            print(e)
            break


    print(f"{name},({player_id}) disconnected")

    connections -= 1
    del players[player_id]
    turn %= len(players)
    conn.close()

print("Waiting for connections")

while True:

    host, addr = sock.accept()
    print(f"Connected to: {addr}")

    connections += 1
    start_new_thread(threaded_client,(host,_id))
    _id += 1
