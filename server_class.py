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
        self.free_parking_amount = 0
        self.game_modes = {"Free Parking": False,
                           "No Sets": False,
                           "Land On GO Get 400": False}

    def no_sets_gamemode(self):
        if self.game_modes["No Sets"]:
            for property in self.board.properties:
                if property.purchase != None:
                    if len(property.rent) > 4:
                        property.full_set = True

    def convert_list(self, player_propertys: list):#this will change the players owned property from Property instances to their index in the Board objects property list
        converted_list = []
        for element in player_propertys:#goes through the set lists in the players owned propertys
            if isinstance(element, list):#returns True if the element is a list, then uses recursion to go through the element as it is a list
                converted_list += self.convert_list(element)
            else:#it is not a list, a single property object
                converted_list.append(self.board.properties.index(element))#converts it to a integer value where it is in the board.properties list
        return converted_list

    def convert_players_for_send(self):
        pl_dict = {}  # need to make function where all stuff that are sent but converted before are converted on one nice function
        for i in list(self.players):  # finds connection id
            pl_index = self.convert_list(self.players[i].owned_propertys)#returns a nested list that contains the index of the players owned propertys in board.propeties list
            pl_dict[i] = list(self.players[i].return_variables())#returns the variables in the player object that can be sent over the network as they are
            pl_dict[i][-1] = pl_index  # makes the owned properties the pl_index list
        return pl_dict

    def convert_auction_for_send(self, pl_list: list):#turns the Auction object from containing player/ property objects to integer values to be sent over the network
        if self.auction is None:#if it is None then no auction is happening
            send_auction = self.auction#send auction becomes None
        else:
            send_auction = (pl_list[self.turn].pos, self.auction.amounts, self.auction.amount, self.auction.turn)#these will all be integer values that can then be turned into the class objects used
        return send_auction

    def convert_deal_for_send(self, pl_list: list):#turns the deal object from containing class objects to integer values
        if self.deal is None:#if it None then no deal is happening
            send_deal = self.deal#send_deal becomes None
        else:
            send_deal = (pl_list.index(self.deal_player), self.convert_list(self.deal.propertys_give),self.convert_list(self.deal.propertys_get),self.deal.money_give, self.deal.money_get)#these are all integer values
        return send_deal

    def convert_turn_for_send(self):#this sends the turn value and whether the game has finished or not
        send_turn = (self.turn, self.check_game_finished())
        return send_turn

    def calculate_turn_number(self, pl_list: list):#uses recursion to find the correct value of turn
        self.turn += 1
        self.turn %= len(pl_list)#loops round the player list when turn goes above the last player in the list
        if pl_list[self.turn].out:#if the player is out then they can not play thus it will go through the function again until it finds a player that is not out
            self.calculate_turn_number(pl_list)

    def calculate_players_out(self):#returns the number of players in the game that can not play
        players_out = 0
        for player_number in list(self.players):#goes through the players
            if self.players[player_number].out:#if out value is True add one to the players_out
                players_out += 1
        return players_out

    def check_game_finished(self):#checks whether there is only one player (or less) that can play and returns True as the game has finished
        players_out = self.calculate_players_out()
        if self.turn != -1 and len(self.players) - players_out <= 1:
            return True
        else:
            return False

    def get_correct_player_data(self, data, player_id):#as only one player, whose turn it is, can perform moves the other players must not be able to interact with the board
        if self.turn == -1:                            #this functions checks whether the player who sent data is allowed to make moves, if it is not their turn then their data becomes
            if self.players[player_id] != list(self.players.values())[0]:
                data = ""#becomes an empty string, does not affect the game
        elif self.action_taken == 4:#if it is a deal then the two players involved can interact in the game
            if self.players[player_id] != self.deal.targeted_player:#if it is not their turn
                data = ""
        elif self.action_taken == 6:#when it is an auction the players take it in turn on the auction to bid but the player who started it hasn't finished their turn so a variable in auction controls whose turn it is
            if list(self.players).index(player_id) != self.auction.turn:#if it is not their turn
                data = ""
        else:#when it will only be controlled by the player whose turn it is
            if list(self.players).index(player_id) != self.turn:#if it is not their turn
                data = ""
        return data

    def set_up_pl_list(self):#turns the player dictionary values into a list and gets the players square co_ords and size
        pl_list = []
        for i in list(self.players):#appends the player object to pl_list
            pl_list.append(self.players[i])
        player_squares = []
        for i in range(len(pl_list)):
            player_squares.append((int(SQUARE_MEASUREMENTS), int(i * SQUARE_MEASUREMENTS / len(pl_list)),int(WINDOW_WIDTH * 29 / 64),int(SQUARE_MEASUREMENTS / len(pl_list))))#this is what the size and position of the player squares will always be no matter how many players there are
        return pl_list, player_squares

    def rolled_a_double(self):#changes values if player rolls a double
        self.triple_checker += 1
        self.double = True

    def rolled_three_doubles(self, pl_list: list):#if player rolls three doubles then they go to jail
        pl_list[self.turn].to_jail()
        self.jail_list.append(pl_list[self.turn])
        self.double = False
        self.action_taken = 1

    def move_player_dice_roll(self, pl_list, roll):#if the player is not in jail or rolled three doubles then they can perform their go
        pl_list[self.turn].move(roll[0])  # when the player clicks roll dice it gets the number and then using the property_action function determines what property has been landed on
        self.action_taken = pl_list[self.turn].property_action(self.board)#returns an integer value corresponding to where the players position is
        if pl_list[self.turn].land_on_go_to_jail():#if they land on the go_to_jail property, the player goes to jail
            self.jail_list.append(pl_list[self.turn])
        if self.game_modes["Land On GO Get 400"]:
            pl_list[self.turn].land_on_go()
        if self.game_modes["Free Parking"]:
            if pl_list[self.turn].land_on_free_parking():
                pl_list[self.turn].money += self.free_parking_amount
                self.free_parking_amount = 0

    def player_rolled_dice(self, roll: list, pl_list: list):
        if roll[1]:#True or False depending on whether the player got a double
            self.rolled_a_double()
        if pl_list[self.turn] in self.jail_list and self.double is False:#if the player is in jail or they have not rolled a double then they can not move
            self.action_taken = 1
            self.jail_list.remove(pl_list[self.turn])
        else:#if the player is not in jail or they rolled a double then the player can move
            if check_for_triple(self.triple_checker):#if triple_checker == 3 returns True
                self.rolled_three_doubles(pl_list)
            else:
                self.move_player_dice_roll(pl_list, roll)

    def reset_for_next_turn(self, pl_list: list):#resets the values that will be changed in the next turn
        if self.double is not True:
            self.calculate_turn_number(pl_list)
            self.triple_checker = 0
        self.other_card = None
        self.double = False
        self.deal_player = None
        self.action_taken = 0  # this will reset it and then let the next player have their turn

    def set_up_deal(self, pl_list: list):#this creates an instance of the Deal class
        if self.deal_player is not None:#if it is None then no player to deal with has been selected
            self.deal = Deal(pl_list[self.turn], self.deal_player, self.board)#creates instance of Deal class
            self.action_taken = 3#this ensures only butttons to do with the deal can be pressed
        else:
            print("select a player, click a player rectangle on the right")

    def go_back(self):#when the data == "BACK" then it needs to go back to the screen displayed before
        if self.action_taken == 5:#this is if a player is on a property when they clicked the Look at properties button
            self.action_taken = 11
        else:#otherwise everywhere where there is an end button it needs to go back to the end screen
            self.action_taken = 1
            self.deal = None
            self.other_card = None

    def declared_bankruptcy(self, player_id: int):#as player is declared out the variables changed by them need to be reset and their properties/ money needs to be removed
        self.players[player_id].remove_assets(self.board, self.have_enough_money)#removes players properties and money
        self.free_parking_amount += self.players[player_id].money
        self.players[player_id].out = True
        self.have_enough_money = True#if a player/tax got the player out then this will be False so needs to be reset
        self.amount_required = 0
        self.double = False

    def close_auction(self, pl_list: list):#when the auction ends the property goes to the players owned_propertys list and the auction is reset
        self.auction.players[self.auction.turn].buy_property(self.board, pl_list[self.turn],self.auction.amount)
        self.auction = None
        self.action_taken = 1#sets to end turn screen

    def display_property_rent(self, pl_list: list):#when player lands on an owned property or tax card it will display the card and money they own
        self.action_time = time.time() if self.action_time == 0 else self.action_time
        if time.time() - self.action_time >= 1.5:#it will keep it at the current action taken value for 1.5 seconds, the property and rent amount will be displayed
            if self.action_taken == 7:#this means a player has landed on an owned property that another player owns
                self.have_enough_money, self.amount_required = pl_list[self.turn].pay_rent(self.board)#checks whether the player can pay the amount, if not then have_enough_money becomes False
            elif self.action_taken == 8:
                self.have_enough_money, self.amount_required, tax_amount = pl_list[self.turn].pay_tax(self.board)
                self.free_parking_amount += tax_amount
            self.action_taken = 1#displays the end turn screen
            self.action_time = 0

    def mouse_pos_player_click(self, data: str, pl_list: list, player_squares:list):#if the player does not click a button but they have clicked the mouse then the mouses co-ordinates are sent over
        x, y = int(data.split(" ")[1]), int(data.split(" ")[2])#the data string sent over is split and the co-ordinate values are taken from the data
        if self.action_taken == 11:#when player clicks LOOK AT PROPERTIES button they can then click on propertys that they own
            if pl_list[self.turn].check_owned_property(x, y):#checks if the player has clicked one of their owned properties
                self.other_card = self.board.properties.index(pl_list[self.turn].check_owned_property(x, y))#makes other_card variable the property the player clicked on
                self.action_taken = 5
        elif self.action_taken == 3:#this is when a deal is going on
            self.deal.add_propertys(x, y)
        for i in range(len(player_squares)):#the player squares is where the information on each player is kept on the right of the screen, this checks if a player has clicked on a player square
            if pygame.Rect(player_squares[i]).collidepoint(x, y) and i != self.turn and not pl_list[i].out:
                self.deal_player = pl_list[i]#makes the deal_player the player stored in the player square that has been clicked on

    def game_finished(self, conn):#when the game is finished it'll keep the players connect for 5 seconds and then disconnect them
        self.action_time = time.time() if self.action_time == 0 else self.action_time
        if time.time() - self.action_time >= 5:
            conn.close()

    def convert_server_variables_for_send(self, pl_list: list):#converts variables so they can be sent to the players
        send_board = self.board.convert_for_send(pl_list)
        pl_dict = self.convert_players_for_send()
        send_auction = self.convert_auction_for_send(pl_list)
        send_deal = self.convert_deal_for_send(pl_list)
        send_turn = self.convert_turn_for_send()
        return send_board, pl_dict, send_auction, send_deal, send_turn

    def join_player_to_game(self, conn, player_id:int, name:str):
        if self.turn == -1:  # this is when the game hasn't officially started and the host is waiting for players to join
            print(f"{name} connected to the server")
            colour = list(COLOURS.values())[player_id % (len(COLOURS) - 1)]  # when player_id goes over the len(COLOURS) it circles back around, the -1 is because the last colour would not show up on the board
            self.players[player_id] = Player(0, 14, colour, starting_money, name, False,[])  # puts the player into the player dictionary
        else:  # if the game has already started then the players connection is closed
            conn.close()
        conn.send(str.encode(str(player_id)))

    def player_move(self, data: str, player_id: int, pl_list:list, player_squares: list, conn):
        #data is what the player has clicked on as a string, this checks the string and performs an action, changes variables depending on what the data variable is
        if self.turn == -1:
            if data == "START" and len(self.players) > 1:
                self.turn = 0  # this will officially start the game and no-one can join
            else:
                for game_mode in list(self.game_modes):
                    if game_mode == data:
                        print("Hello")
                        if self.game_modes[game_mode]:
                            self.game_modes[game_mode] = False
                        else:
                            self.game_modes[game_mode] = True
        elif data == "ROLL DICE":#when the player starts their turn
            roll = dice_roll()
            self.player_rolled_dice(roll, pl_list)
        #end turn resets values and moves onto the next turn
        elif data == "END TURN" and self.have_enough_money is True:#if have_enough_money is False then the player owes money and can not end their turn
            self.reset_for_next_turn(pl_list)
            self.no_sets_gamemode()

        elif data == "MAKE DEAL":#when a player wants to deal with another player
            self.set_up_deal(pl_list)

        elif data == "LOOK AT PROPERTIES":#at the end turn screen, this will then allow players to select a property they own and from there can mortgage, unmortgage and add/takeway houses
            self.action_taken = 11

        elif data == "PURCHASE":#when a player lands on an unowned property and they want to buy it
            if pl_list[self.turn].buy_property(self.board):
                self.action_taken = 1
                self.board.utility_station_rent("BLACK")#as the station and utility rent work differently then whenever a property is exchanged it checks and changes the houses value
                self.board.utility_station_rent("BOARD COLOUR")

        elif data == "AUCTION":#when a player lands on an unowned property and they dont have enough money or do not want to buy it then an auction must happen
            self.auction = Auction(pl_list, pl_list[self.turn].pos, self.board)
            self.action_taken = 6
            self.board.utility_station_rent("BLACK")
            self.board.utility_station_rent("BOARD COLOUR")

        elif data == "BID 1":#during the auction the players can click BID 1,10,100 this will add the amount to the total amount
            self.auction.add_amount(1)

        elif data == "BID 10":
            self.auction.add_amount(10)

        elif data == "BID 100":
            self.auction.add_amount(100)

        elif data == "LEAVE":#leave is used if a player no longer wants to be in an auction
            self.auction.leave()

        elif data == "BACK":#back button appears when player clicks on LOOK AT PROPERTIES or MAKE DEAL it will take them back to the page displayed before
            self.go_back()

        elif data == "+ HOUSE":#when a player has selected one of their properties to look at they then have different choices on what they can do to it
            pl_list[self.turn].add_house(self.board, self.other_card)

        elif data == "- HOUSE":
            pl_list[self.turn].remove_house(self.board, self.other_card)

        elif data == "MORTGAGE":
            pl_list[self.turn].mortgage(self.board, self.other_card)

        elif data == "UNMORTGAGE":
            pl_list[self.turn].unmortgage(self.board, self.other_card)

        elif data == "FINISHED":#during a Deal this is used when the player has decided what they want to trade.
            self.action_taken = 4

        elif "+1" in data or "-1" in data:#during a deal a player selects how much money they want to give or get
            self.deal.change_money(data)

        elif data == "ACCEPT":#when the player who started the deal clicks FINISHED, the player who is being traded with can then accept the deal or reject it
            self.action_taken = 1
            self.deal.accept()
            self.deal = None
            self.board.utility_station_rent("BLACK")
            self.board.utility_station_rent("BOARD COLOUR")

        elif data == "REJECT":#this will reject a proposed deal
            self.action_taken = 1
            self.deal = None

        elif data == "BANKRUPT":#when a player does not have enough money to pay another players rent they will declare bankruptcy and be out of the game
            self.declared_bankruptcy(player_id)
            self.reset_for_next_turn(pl_list)
            self.board.utility_station_rent("BLACK")
            self.board.utility_station_rent("BOARD COLOUR")

        elif self.action_taken == 6:#when action taken is 6 a deal is going on
            if self.auction.check_finished():
                self.close_auction(pl_list)

        elif self.action_taken == 7 or self.action_taken == 8 or self.action_taken == 9:#when action taken is 7, 8 or 9 it represents rent, tax and community chest respectively
            self.display_property_rent(pl_list)

        elif data.split(" ")[0] == "mousepos":  #if the data starts with mousepos then no button has been clicked but the player has still clicked, thus the mouse co-ordinates are sent over
            self.mouse_pos_player_click(data, pl_list, player_squares)

        if self.check_game_finished():
            self.game_finished(conn)

        if pl_list[self.turn].money - self.amount_required >= 0 and self.action_taken == 1 and self.have_enough_money is False:#when a player does not have enough money when they have to pay rent/tax they can still get money to pay thus this checks whether they have aquired enough money and allows the transaction to happen if they do
            self.action_taken = pl_list[self.turn].property_action(self.board)

        send_board, pl_dict, send_auction, send_deal, send_turn = self.convert_server_variables_for_send(pl_list)
        if self.turn == -1:
            data_to_send = send_board, self.action_taken, pl_dict, send_turn, self.other_card, send_deal, send_auction, list(self.game_modes.values())
        else:
            data_to_send = send_board, self.action_taken, pl_dict, send_turn, self.other_card, send_deal, send_auction
        data_send = pickle.dumps((data_to_send))#sends game info to the clients/players

        conn.send(data_send)

    def reset_player_propertys(self, player_id):#when a player disconnects and no-one got them out then their propertys are reset
        for props in self.board.properties:
            if props.owned != None:
                if props.owned == self.players[player_id]:
                    props.owned = None#changes the propertys owned status to None as that is what it was when the game started

    def disconnect_player(self, player_id, pl_list, conn):#if a player disconnects they need to be declared out in the game and then carry on with the next players turn
        if self.turn == -1:#as the game hasn't started they are removed so another player can join
            del self.players[player_id]
        else:
            self.players[player_id].out = True#sets the players to out
            self.players[player_id].owned_propertys = []#removes the players propertys
        if len(self.players) - self.calculate_players_out() > 1 and self.turn != -1:#changes turn unless the game has finished
            self.calculate_turn_number(pl_list)
        conn.close()#disconnects the player


    def threaded_client(self, conn, id: int):#main function where the players will have their own thread and play the game
        player_id = id  # becomes the number of how many have connected to the server, when the player connects
        data = conn.recv(16)  # recieve data from the client, this will be their chosen name
        name = data.decode("utf-8")
        self.join_player_to_game(conn, player_id, name)

        pl_list = []

        if __name__ == "__main__":
            while True:
                try:
                    pl_list, player_squares = self.set_up_pl_list()#returns a lsit of the players and a list of the player squares position and size

                    data = conn.recv(32)#recieve data from the client


                    if not data:#if nothing is recieved then there is an error so this thread must be closed and the player connected to the thread will be disconnected
                        break
                    else:
                        data = data.decode("utf-8")#decodes the data into a string
                        data = self.get_correct_player_data(data, player_id)#checks who sent it and whether it is their turn or not

                    self.player_move(data, player_id, pl_list, player_squares, conn)#pus the data in here and checks what has been sent and then performs an action based on what the client/player has done

                except Exception as e:#if there is an error in recieving and processing the data then it breaks the game loop and disconnects the player
                    print(e)
                    print(traceback.format_exc())
                    break

            if list(self.players.values())[self.turn] == self.players[player_id]:#if it is the players turn who is about to be disconnected then it resets to start the players turn otherwise there will be an error
                self.action_taken = 0

            print(f"{name},({player_id}) disconnected")

            self.connections -= 1#as player will disconnect there will be one less connection to the server
            if self.have_enough_money is True:#this means the player did not owe money to another player or tax card
                self.reset_player_propertys(player_id)#resets there property owned status, how many houses to their state when the game began
            else:#player or tax card got them out so their properties and money need to exchange hands
                self.declared_bankruptcy(player_id)
            self.disconnect_player(player_id, pl_list, conn)#disconnects the player from the game


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

HOST = '192.168.1.150'  #the host where the server is run from and the clients/ players connect to
PORT = 5672  #Port to listen on

try:
    sock.bind((HOST, PORT))
except socket.error as e:
    print(str(e))
    print("Server did not start")
    quit()

sock.listen(6)#allows clients/players to join

print(f"server started with IP-{HOST}")

# variables that change
server = Server()#initiate server class
id_ = 0
print("Waiting for connections")

while True:

    host, addr = sock.accept()#accepting connection to server
    print(f"Connected to: {addr}")
    if server.connections == 0:
        server = Server()
    server.connections += 1
    start_new_thread(server.threaded_client, (host, id_))#start a new thread so all the clients can interact with the server at the same time
    id_ += 1
