import time
from constants import *
from _thread import *
import _pickle as pickle
import socket
from game_rules import *
from player import Auction, Deal, Player
import traceback


class Server():
    def __init__(self):  # these are all the variables that could change across the course of the game and need to stay the same for every player
        self.board = Board(WINDOW_WIDTH, SQUARE_MEASUREMENTS)
        self.players = {}#dictionary that contains the player_id as the key and then their player object as the value
        self.connections = 0#when the server starts there will always be 0 connections
        self.action_taken = 0#controls what is drawn and what a player can do
        self.triple_checker = 0#if the number reaches three then they have got 3 doubles in a row a must go to jail
        self.jail_list = []#player gets appended here if they land on go to jail or get three doubles in a row
        self.double = False#if a player gets a double it becomes True and then False when they take their next turn
        self.turn = -1 #this controls which players turn it is, the -1 value means the game has not started
        self.have_enough_money = True#when the player lands on a owned/ tax property and they can not afford the rent this will become False
        self.other_card = None#if the game is on another card that the player whose turn it is, is not on then this becomes the property object they are on
        self.action_time = 0#this will be used for a timer
        self.amount_required = 0#if a player can not pay rent/tax this will become the value they need to be able to pay them
        self.auction = None #this will change to an Auction object when an auction begins
        self.deal = None #this will change to a Deal object when a deal begins
        self.deal_player = None #when a player selects who they want to deal with it will become a player object

    def convert_list(self, start_list):
        converted_list = []
        for element in start_list:
            if isinstance(element, list):
                converted_list += self.convert_list(element)
            else:
                converted_list.append(self.board.properties.index(element))
        return converted_list

    def convert_players_for_send(self):
        pl_dict = {}  # need to make function where all stuff that are sent but converted before are converted on one nice function
        for i in list(self.players):  # finds connection id
            pl_index = self.convert_list(self.players[i].owned_propertys)
            pl_dict[i] = list(self.players[i].return_variables())
            pl_dict[i][-1] = pl_index  # makes the owned propertys the pl_index list
        return pl_dict

    def convert_auction_for_send(self, pl_list):
        if self.auction is None:
            send_auction = self.auction
        else:
            send_auction = (pl_list[self.turn].pos, self.auction.amounts, self.auction.amount, self.auction.turn)
        return send_auction

    def convert_deal_for_send(self, pl_list):
        if self.deal is None:
            send_deal = self.deal
        else:
            send_deal = (
                pl_list.index(self.deal_player), self.convert_list(self.deal.propertys_give),
                self.convert_list(self.deal.propertys_get),
                self.deal.money_give, self.deal.money_get)
        return send_deal

    def convert_turn_for_send(self, check_game_finished):
        if check_game_finished:
            send_turn = (self.turn, True)
        else:
            send_turn = (self.turn, False)
        return send_turn

    def calculate_turn_number(self, pl_list):
        self.turn += 1
        self.turn %= len(pl_list)
        if pl_list[self.turn].out:
            self.calculate_turn_number(pl_list)

    def calculate_players_out(self):
        players_out = 0
        for player_number in list(self.players):
            if self.players[player_number].out:
                players_out += 1
        return players_out

    def check_game_finished(self):
        players_out = self.calculate_players_out()
        if self.turn != -1 and len(self.players) - players_out <= 1:
            return True
        else:
            return False

    def check_for_reset(self):
        if self.connections == 0 and self.turn != -1:
            return True
        else:
            return False

    def get_correct_player_data(self, data, player_id):
        if self.turn == -1:
            if data == "START":
                self.turn = 0
            else:
                data = ""
        if self.action_taken == 4:
            if self.players[player_id] != self.deal.targeted_player:
                data = ""
        elif self.action_taken == 6:
            if list(self.players).index(player_id) != self.auction.turn:
                data = ""
        else:
            if list(self.players).index(player_id) != self.turn:
                data = ""
        return data

    def threaded_client(self, conn, id: int):

        player_id = id

        # get name from client
        data = conn.recv(16)
        name = data.decode("utf-8")
        if self.turn == -1:
            print(f"{name} connected to the server")
            # setting up player
            colour = list(COLOURS.values())[player_id]
            self.players[player_id] = Player(0, 14, colour, starting_money, name, False, [])
        else:
            conn.close()

        conn.send(str.encode(str(player_id)))

        pl_list = []

        while True:
            try:
                # while loop here to holt gameplay until host says start game and everyone joins
                pl_list = []
                for i in list(self.players):
                    pl_list.append(self.players[i])
                player_squares = []
                for i in range(len(pl_list)):
                    player_squares.append((int(SQUARE_MEASUREMENTS), int(i * SQUARE_MEASUREMENTS / len(pl_list)),
                                           int(WINDOW_WIDTH * 29 / 64),
                                           int(SQUARE_MEASUREMENTS / len(pl_list))))
                # recieve from client
                data = conn.recv(32)

                if not data:
                    break
                else:
                    data = data.decode("utf-8")
                    data = self.get_correct_player_data(data, player_id)





                """This is where you recieve info from the clients and send it back
                """

                if data == "ROLL DICE":
                    roll = dice_roll()
                    if roll[1]:
                        self.triple_checker += 1
                        self.double = True
                    if pl_list[self.turn] not in self.jail_list or self.double is True:
                        if not check_for_triple(self.triple_checker):
                            pl_list[self.turn].move(roll[
                                                        0])  # when the player clicks roll dice it gets the number and then using the property_action function determines what property has been landed on
                            self.action_taken = pl_list[self.turn].property_action(self.board)
                        else:
                            pl_list[self.turn].to_jail()
                            self.jail_list.append(pl_list[self.turn])
                            self.double = False
                            self.action_taken = 1
                    else:
                        self.action_taken = 1
                        self.jail_list.remove(pl_list[self.turn])

                elif data == "END TURN" and self.have_enough_money is True:
                    if self.double is not True:
                        self.calculate_turn_number(pl_list)
                        self.triple_checker = 0
                    self.other_card = None
                    self.double = False
                    self.deal_player = None
                    self.action_taken = 0  # this will reset it and then let the next player have their turn

                elif data == "MAKE DEAL":
                    if self.deal_player is not None:
                        self.deal = Deal(pl_list[self.turn], self.deal_player, self.board)
                        self.action_taken = 3
                    else:
                        print("select a player, click a player rectangle on the right")

                elif data == "LOOK AT PROPERTIES":
                    self.action_taken = 11

                elif data == "PURCHASE":
                    if pl_list[self.turn].buy_property(self.board):
                        self.action_taken = 1

                elif data == "AUCTION":
                    self.auction = Auction(pl_list, pl_list[self.turn].pos, self.board)
                    self.action_taken = 6

                elif data == "BID 1":
                    self.auction.add_amount(1)

                elif data == "BID 10":
                    self.auction.add_amount(10)

                elif data == "BID 100":
                    self.auction.add_amount(100)

                elif data == "LEAVE":
                    self.auction.leave()

                elif data == "BACK":
                    if self.action_taken == 5:
                        self.action_taken = 11
                    else:
                        self.action_taken = 1
                        self.deal = None
                        self.other_card = None

                elif data == "+ HOUSE":
                    pl_list[self.turn].add_house(self.board, self.other_card)

                elif data == "- HOUSE":
                    pl_list[self.turn].remove_house(self.board, self.other_card)

                elif data == "MORTGAGE":
                    pl_list[self.turn].mortgage(self.board, self.other_card)

                elif data == "UNMORTGAGE":
                    pl_list[self.turn].unmortgage(self.board, self.other_card)

                elif data == "FINISHED":
                    self.action_taken = 4

                elif "+1" in data or "-1" in data:
                    self.deal.change_money(data)

                elif data == "ACCEPT":
                    self.action_taken = 1
                    self.deal.accept()
                    self.deal = None

                elif data == "REJECT":
                    self.action_taken = 1
                    self.deal = None

                elif data == "BANK":
                    # function that takes in have_enough_money variable to decide whether another player takes there propertys else it goes to the bank and free parking
                    pl_list[self.turn].remove_assets(self.board, self.have_enough_money)
                    self.players[player_id].out = True
                    self.calculate_turn_number(pl_list)
                    self.triple_checker = 0
                    self.other_card = None
                    self.double = False
                    self.deal_player = None
                    self.action_taken = 0
                    self.have_enough_money = True

                elif data == "START":
                    self.turn = 0

                elif self.action_taken == 6:
                    if self.auction.check_finished():
                        self.auction.players[self.auction.turn].buy_property(self.board, pl_list[self.turn],
                                                                             self.auction.amount)
                        self.auction = None
                        self.action_taken = 1


                elif self.action_taken == 7 or self.action_taken == 8 or self.action_taken == 9:
                    self.action_time = time.time() if self.action_time == 0 else self.action_time
                    if time.time() - self.action_time >= 1.5:
                        if self.action_taken == 7:
                            self.have_enough_money, self.amount_required = pl_list[self.turn].pay_rent(self.board)
                        elif self.action_taken == 8:
                            self.have_enough_money, self.amount_required = pl_list[self.turn].pay_tax(self.board)
                        self.action_taken = 1
                        self.action_time = 0

                elif data.split(" ")[0] == "mousepos":  # when in look at propertys, click on owned property and it is displayed
                    x, y = int(data.split(" ")[1]), int(data.split(" ")[2])
                    if self.action_taken == 11:
                        if pl_list[self.turn].check_owned_property(x, y):
                            self.other_card = self.board.properties.index(pl_list[self.turn].check_owned_property(x, y))
                            self.action_taken = 5
                    elif self.action_taken == 3:
                        self.deal.add_propertys(x, y)
                    for i in range(len(player_squares)):
                        if pygame.Rect(player_squares[i]).collidepoint(x, y) and i != self.turn:
                            self.deal_player = pl_list[i]

                if self.check_game_finished():
                    self.action_time = time.time() if self.action_time == 0 else self.action_time
                    if time.time() - self.action_time >= 5:
                        conn.close()
                if pl_list[self.turn].land_on_go_to_jail():
                    self.jail_list.append(pl_list[self.turn])

                self.board.utility_station_rent("BLACK")
                self.board.utility_station_rent("BOARD COLOUR")

                if pl_list[
                    self.turn].money - self.amount_required >= 0 and self.action_taken == 1 and self.have_enough_money is False:
                    self.action_taken = pl_list[self.turn].property_action(self.board)

                send_board = self.board.convert_for_send(pl_list)

                pl_dict = self.convert_players_for_send()

                send_auction = self.convert_auction_for_send(pl_list)

                send_deal = self.convert_deal_for_send(pl_list)

                send_turn = self.convert_turn_for_send(self.check_game_finished())

                data_send = pickle.dumps(
                    (send_board, self.action_taken, pl_dict, send_turn, self.other_card, send_deal, send_auction))

                conn.send(data_send)


                print(self.connections)



            except Exception as e:
                print(e)
                print(traceback.format_exc())
                break

        if list(self.players.values())[self.turn] == self.players[player_id]:
            self.action_taken = 0

        print(f"{name},({player_id}) disconnected")

        self.connections -= 1


        for props in self.board.properties:
            if props.owned != None:
                if props.owned == self.players[player_id]:
                    props.owned = None

        if self.turn == -1:
            del self.players[player_id]
        else:
            self.players[player_id].out = True
            self.players[player_id].owned_propertys = []
        if len(self.players) - self.calculate_players_out() > 1 and self.turn != -1:
            self.calculate_turn_number(pl_list)
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
server = Server()
id_ = 0
print("Waiting for connections")

while True:

    host, addr = sock.accept()
    print(f"Connected to: {addr}")
    if server.connections == 0:
        server = Server()
    server.connections += 1
    start_new_thread(server.threaded_client, (host, id_))
    id_ += 1
