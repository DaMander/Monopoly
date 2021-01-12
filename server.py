import time
from constants import *
from _thread import *
import _pickle as pickle
import socket
from game_rules import *
from player import Auction, Deal, Player
import traceback


def set_board():
    board = Board(WINDOW_WIDTH, SQUARE_MEASUREMENTS)
    board.sort_sets()
    return board


def convert_list(start_list):
    converted_list = []
    for element in start_list:
        if isinstance(element, list):
            converted_list += convert_list(element)
        else:
            converted_list.append(board.properties.index(element))
    return converted_list


def calculate_turn_number(turn, pl_list):
    turn += 1
    turn %= len(pl_list)
    if pl_list[turn].out:
        turn = calculate_turn_number(turn, pl_list)
    return turn


def calculate_players_out():
    players_out = 0
    for player_number in list(players):
        if players[player_number].out:
            players_out += 1
    return players_out


def check_game_finished():
    players_out = calculate_players_out()
    if turn != -1 and len(players) - players_out <= 1:
        return True


def check_for_reset():
    if connections == 0 and turn != -1:
        return True
    else:
        return False


def reset_game():
    reset_board = set_board()
    reset_players = {}
    reset_turn = -1
    return reset_board, reset_players, reset_turn


def threaded_client(conn, _id):
    global players, connections, action_taken, triple_checker, jail_list, double, turn, have_enough_money, other_card, action_time, amount_required, auction, deal, deal_player

    player_id = _id

    # get name from client
    data = conn.recv(16)
    name = data.decode("utf-8")
    if turn == -1:
        print(f"{name} connected to the server")
        # setting up player
        colour = list(COLOURS.values())[player_id]
        players[player_id] = Player(0, 14, colour, starting_money, name, False, [])
    else:
        conn.close()

    action_time = 0

    conn.send(str.encode(str(player_id)))

    while True:
        try:
            # while loop here to holt gameplay until host says start game and everyone joins
            pl_list = []
            for i in list(players):
                pl_list.append(players[i])
            player_squares = []
            for i in range(len(pl_list)):
                player_squares.append((int(SQUARE_MEASUREMENTS), int(i * SQUARE_MEASUREMENTS / len(pl_list)),
                                       int(WINDOW_WIDTH*29/64),
                                       int(SQUARE_MEASUREMENTS / len(pl_list))))
            # recieve from client
            data = conn.recv(32)

            if not data:
                break

            data = data.decode("utf-8")
            if turn == -1:
                if data == "START":
                    turn = 0
                else:
                    data = ""
            if (list(players).index(player_id) != turn and (action_taken != 6 and action_taken != 4)) or (
                    action_taken == 6 and list(players).index(player_id) != auction.turn) or (
                    action_taken == 4 and players[player_id] != deal.targeted_player):
                data = ""

            if action_taken == 3:
                print(deal.player.username)
                print(deal.targeted_player.username, "******")

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

            elif data == "END TURN" and have_enough_money is True:
                if double is not True:
                    turn = calculate_turn_number(turn, pl_list)
                    triple_checker = 0
                other_card = None
                double = False
                deal_player = None
                action_taken = 0  # this will reset it and then let the next player have their turn

            elif data == "MAKE DEAL":
                if deal_player is not None:
                    deal = Deal(pl_list[turn], deal_player, board)
                    action_taken = 3
                else:
                    print("select a player, click a player rectangle on the right")

            elif data == "LOOK AT PROPERTIES":
                action_taken = 11

            elif data == "PURCHASE":
                if pl_list[turn].buy_property(board):
                    action_taken = 1

            elif data == "AUCTION":
                auction = Auction(pl_list, pl_list[turn].pos, board)
                action_taken = 6

            elif data == "BID 1":
                auction.add_amount(1)

            elif data == "BID 10":
                auction.add_amount(10)

            elif data == "BID 100":
                auction.add_amount(100)

            elif data == "LEAVE":
                auction.leave()

            elif data == "BACK":
                if action_taken == 5:
                    action_taken = 11
                else:
                    action_taken = 1
                    deal = None
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

            elif "+1" in data or "-1" in data:
                deal.change_money(data)

            elif data == "ACCEPT":
                action_taken = 1
                deal.accept()
                deal = None

            elif data == "REJECT":
                action_taken = 1
                deal = None

            elif data == "BANK":
                # function that takes in have_enough_money variable to decide whether another player takes there propertys else it goes to the bank and free parking
                pl_list[turn].remove_assets(board, have_enough_money)
                players[player_id].out = True
                turn = calculate_turn_number(turn, pl_list)
                triple_checker = 0
                other_card = None
                double = False
                deal_player = None
                action_taken = 0
                have_enough_money = True

            elif data == "START":
                turn = 0

            elif action_taken == 6:
                if auction.check_finished():
                    auction.players[0].buy_property(board, pl_list[turn], auction.amount)
                    action_taken = 1


            elif action_taken == 7 or action_taken == 8 or action_taken == 9:
                action_time = time.time() if action_time == 0 else action_time
                if time.time() - action_time >= 1.5:
                    if action_taken == 7:
                        have_enough_money, amount_required = pl_list[turn].pay_rent(board)
                    elif action_taken == 8:
                        have_enough_money, amount_required = pl_list[turn].pay_tax(board)
                    action_taken = 1
                    action_time = 0

            elif data.split(" ")[0] == "mousepos":  # when in look at propertys, click on owned property and it is displayed
                x, y = int(data.split(" ")[1]), int(data.split(" ")[2])
                if action_taken == 11:
                    if pl_list[turn].check_owned_property(x, y):
                        other_card = board.properties.index(pl_list[turn].check_owned_property(x, y))
                        action_taken = 5
                elif action_taken == 3:
                    deal.add_propertys(x, y)
                for i in range(len(player_squares)):
                    if pygame.Rect(player_squares[i]).collidepoint(x, y) and i != turn:
                        deal_player = pl_list[i]

            if check_game_finished():
                action_time = time.time() if action_time == 0 else action_time
                print(time.time() - action_time)
                if time.time() - action_time >= 5:
                    conn.close()

            if pl_list[turn].land_on_go_to_jail(board):
                jail_list.append(pl_list[turn])

            board.utility_station_rent("BLACK")
            board.utility_station_rent("BOARD COLOUR")

            if pl_list[turn].money - amount_required >= 0 and action_taken == 1 and have_enough_money is False:
                action_taken = pl_list[turn].property_action(board)

            send_board = board.convert_for_send(pl_list)

            pl_dict = {}  # need to make function where all stuff that are sent but converted before are converted on one nice function
            for i in list(players):  # finds connection id
                pl_index = convert_list(players[i].owned_propertys)
                pl_dict[i] = list(players[i].return_variables())
                pl_dict[i][-1] = pl_index  # makes the owned propertys the pl_index list

            if auction is None:
                send_auction = auction
            else:
                send_auction = (pl_list[turn].pos, auction.amounts, auction.amount, auction.turn)

            if deal is None:
                send_deal = deal
            else:
                send_deal = (
                pl_list.index(deal_player), convert_list(deal.propertys_give), convert_list(deal.propertys_get),
                deal.money_give, deal.money_get)

            if check_game_finished():
                send_turn = (turn, True)
            else:
                send_turn = (turn, False)

            data_send = pickle.dumps(
                (send_board, action_taken, pl_dict, send_turn, other_card, send_deal, send_auction))

            conn.send(data_send)






        except Exception as e:
            print(e)
            print(traceback.format_exc())
            break

    if list(players.values())[turn] == players[player_id]:
        action_taken = 0

    print(f"{name},({player_id}) disconnected")

    connections -= 1

    for props in board.properties:
        if props.owned != None:
            if props.owned == players[player_id]:
                props.owned = None

    if turn == -1:
        del players[player_id]
    else:
        players[player_id].out = True
        players[player_id].owned_propertys = []
    if len(players) - calculate_players_out() > 1 and turn != -1:
        turn = calculate_turn_number(turn, pl_list)
    conn.close()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

HOST = '192.168.1.150'  # local host
PORT = 5672  # Port to listen on

try:
    sock.bind((HOST, PORT))
except socket.error as e:
    print(str(e))
    print("Server did not start")
    quit()

sock.listen(6)

print(f"server started with IP-{HOST}")

# variables that change
connections = 0
_id = 0
print("Waiting for connections")

while True:

    host, addr = sock.accept()
    print(f"Connected to: {addr}")
    if connections == 0:
        board = set_board()
        players = {}
        turn = -1
    connections += 1
    start_new_thread(threaded_client, (host, _id))
    _id += 1
