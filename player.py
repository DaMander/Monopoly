from constants import *
pygame.font.init()
font = pygame.font.SysFont('arial', 26)


#the player class primarily will include decisions that relate to the player for instance when buying a property, although it involves the board it is primarily affected by the player


class Player:
    def __init__(self, pos:int, radius:int, colour:tuple, money:int, username:str, out:bool, propertys:list):
        self.pos = pos
        self._radius = radius
        self.colour = colour
        self.money = money
        self.username = username
        self.out = out
        self.owned_propertys = propertys

        #add list which uses the thing to add propertys to create the list with every set

    def check_they_can_pay(self, figure:int):#checks if a player has enough money if they try to buy something
        if self.money - figure >= 0:
            return True
        else:
            return False

    def draw(self, win):#draws the player to the screen, their circle icon
        space = win.properties[self.pos]
        x, y = pygame.Rect(space.x, space.y, space.get_rect().w, space.get_rect().h).center
        pygame.draw.circle(win, self.colour, (x, y), self._radius)
        pygame.draw.circle(win, COLOURS["BLACK"], (x,y), self._radius,1)

    def draw_player_square(self, win, player_index, height, turn):#draws the squares which contains player name, money and properties they own
        player_square = (SQUARE_MEASUREMENTS, player_index * height, WINDOW_WIDTH*29/64, height)
        self.draw_player_name_and_money(win, player_square, player_index, height, turn)
        self.draw_player_propertys(win, player_square, player_index, height)


    def draw_player_name_and_money(self,win,player_square:tuple,player_index: int,height: int, turn:int):#draws the players name and money within their square
        pygame.draw.rect(win, COLOURS["GREEN"], player_square, 5) if turn == player_index else None
        pygame.draw.rect(win, COLOURS["BLACK"], player_square, 1)
        x,y = pygame.Rect(player_square).center
        render_text(win, font, self.username, self.colour,(x - WINDOW_WIDTH * 29 / 256, y - height / 4))
        render_text(win, font, str(int(self.money)), COLOURS["BLACK"],(x, y - height / 4))

    def draw_player_propertys(self, win, player_square: tuple, player_index: int, height: int):#draws the colours of the properties the player owns
        set_dist = 0
        for sets in self.owned_propertys:#goes through the groups of properties each list contains the colour set
            set_dist += 1# sets are alligned horizontally as you look left to right in the player square there will be new sets
            prop_dist = 0
            for p in sets:#goes through the properties within that set and draws them to the screen.
                x,y = pygame.Rect(player_square).midleft
                pygame.draw.rect(win, p.colour, (x + set_dist * WINDOW_WIDTH*5/256,y + prop_dist * WINDOW_WIDTH*5/256, WINDOW_WIDTH*1/64, WINDOW_WIDTH*1/64))
                pygame.draw.rect(win, COLOURS["BLACK"], (x + set_dist * WINDOW_WIDTH*5/256,y + prop_dist * WINDOW_WIDTH*5/256, WINDOW_WIDTH*1/64, WINDOW_WIDTH*1/64), 1)
                prop_dist += 1 #if their are multiple properties within the same set then they're drawn below each other
        if self.out:
            pygame.draw.line(win, COLOURS["RED"], (SQUARE_MEASUREMENTS, player_index * height), (SQUARE_MEASUREMENTS + WINDOW_WIDTH * 29 / 64, player_index * height + height), 5)

    def check_rect(self, rect: tuple):#checks if player co-ordinates are within a rectangle
        x,y = pygame.mouse.get_pos()
        return pygame.Rect(rect).collidepoint(x,y)

    def property_action(self, win):#finds out which property the player has landed on and what action will take place on that property
        print(self.pos)
        action = win.properties[self.pos].property_actions(self)#returns an integer
        return action


    def move(self, amount: int):
        if self.pos + amount > 39:#the player has got to the end of the board
            self.pos = (self.pos + amount) - 40 #at the start of the board on the property if they counted round the board corner
            self.pass_go()
        else:
            self.pos += amount

    def pass_go(self): #pass go and the player gets 200 money
        self.money += 200

    def add_property(self, property, win):#checks if the player already has a property of the same colour and adds it to the list it's in
        added = False                     #if it doesn't then it appends it to their owned propertys and sorts in order of front to end of board
        for set in self.owned_propertys:
            if added:#if the property set has been found then break for loop as there is no need to carry on
                break
            for p in set:
                if p.colour == property.colour: #if the property colour is the same as the colour in a set then the property belongs in that set
                    set.append(property)
                    added = True
                    if self.check_for_full_set(win, set): #as it is adding into an already existing set then it will check if the player owns a full set
                        for prop in set:
                            prop.full_set = True
                break  # this will check through the propertys owned and if the colour is the same then it will append it into the list otherwise it'll just add it
        if added is False: #this means the colour set does not already exist
            property.full_set = False #if the player does a deal and it was in a full set then it would still be True so it's reset
            self.owned_propertys.append([property])
            self.owned_propertys.sort(key= lambda x: win.properties.index(x[0]))#this sorts the players owned propertys into the order that they are on the board

    def remove_property(self, property):#if a player gets rid of a property then this will remove it from their owned properties
        for set in self.owned_propertys:
            if property in set:
                set.remove(property)
                self.no_full_set(set)
                break
        self.owned_propertys = [i for i in self.owned_propertys if i]#go through the owned properties list and remove any empty lists

    def no_full_set(self, set:list):#if a property from the set is removed then it is no longer a complete set and they will be reset
        for property in set:
            property.full_set = False

    def check_for_full_set(self, win, set):#checks if a players set matches the actual set needed for a full set
        set_colour = list(COLOURS)[list(COLOURS.values()).index(set[0].colour)]#returns the key of the COLOURS dictionary for colour set needed
        if all(elem in set for elem in win.SORTED_SETS[set_colour]):#this statement returns True if all the elements of the players set are in the actual set
            return True
        else:
            return False

    def check_owned_property(self,x:int,y:int):#checks if a players x and y co-ordinate are on a property if they are it returns the instance of the property class they're mouse is over
        for sets in self.owned_propertys:
            for p in sets:
                if pygame.Rect(p.x, p.y, p.width, p.height).collidepoint(x,y):
                    return p

    def buy_property(self, win, other_player = None, amount:int = None):#checks if player can afford property if they can they aquire the property and loose the amount it costs
        #when this is but into the main function the win will become the instance of the board class so the player and board can work in unison
        space = win.properties[self.pos if other_player is None else other_player.pos]#finding the property instance being bought
        amount = space.purchase if amount is None else amount
        print(amount)
        if self.check_they_can_pay(amount):#returns True if they have enough money to pay for it
            self.money -= amount
            self.add_property(space,win)#adds property to players owned properties
            space.owned = self#properties owned status becomes the player object
            return True
        else:
            return False


    def pay_rent(self, win, roll:int):#finds out how much the player looses, gives it to the property's owner and checks if they can pay
        #this will be used to player who owns the property that the current player has landed on and tax that the player lands on
        space = win.properties[self.pos]
        if space.owned != self and space.mortgage is not True:#if property is mortgaged or the player owns it then they can't pay rent
            rent = space.rent[str(space.amount_houses)]#accessing the property amount of houses which is a dictionary to find amount needed to pay
            if space.colour == COLOURS["BOARD COLOUR"]:
                rent = rent*roll
            elif space.full_set is True and space.amount_houses == 0:
                rent *= 2#if player owns full set but no houses then rent is doubled
            if self.check_they_can_pay(rent):
                self.money -= rent
                space.owned.money += rent #gives the player who owns the property the required rent
                return True, 0
            else:
                return False, rent
            #TODO create function that will identify utility card and then x by dice roll

    def pay_tax(self, win):#if player lands on tax, checks if they can pay and if they can takes the required money away if not returns False and amount they need
        space = win.properties[self.pos]
        rent = space.rent#gets rent amount
        if self.check_they_can_pay(rent):#checks they have enough money to pay
            self.money -= rent
            return True, 0, rent
        else:
            return False, rent, 0

    def check_houses_can_be_altered(self, current_property, add_or_remove: str):#this function checks whether the player can remove or add houses to a property
        full_set = current_property.full_set #full set will be either True or False
        mortgage = current_property.mortgage #mortgage value will be False if it is not mortgaged
        houses = current_property.amount_houses #this will be an integer from 0 to 5
        if full_set and not mortgage: #to add or remove houses the player needs a full set and the property can not be mortgaged
            if add_or_remove == "ADD":
                if houses < 5 and self.money >= current_property.houses_price: #to add a house the houses need to be less than 5 and the the player needs to be able to afford the house
                    return True
                else:
                    return False
            else:
                if houses > 0:#to remove the property needs to have 1 or more houses
                    return True
                else:
                    return False

    def add_house(self, win, pos): #increase the amount_houses value of the property object by 1
        current_property = win.properties[pos]
        if self.check_houses_can_be_altered(current_property, "ADD"): #returns True if houses can be added
            self.money -= current_property.houses_price #removes amount houses cost from player
            current_property.amount_houses += 1

    def remove_house(self, win, pos):#decreases the amount_houses of the property object by 1
        current_property = win.properties[pos]
        if self.check_houses_can_be_altered(current_property, "REMOVE"): #returns True if they can be removed
            self.money += current_property.houses_price/2 #gives player half the amount it would cost to buy the propertys house
            current_property.amount_houses -= 1

    def mortgage(self, win, pos): #changes the mortgage value of the property object to True if it can be mortgaged
        current_property = win.properties[pos]
        if not current_property.mortgage and (current_property.amount_houses == 0 or current_property.houses_price is None):#if it has no houses then it can be mortgage and if it has no house price it means it's a station or utility
            self.money += current_property.purchase/2 #recieve half the propertys purchase value
            current_property.mortgage = True

    def unmortgage(self, win, pos):#changes the mortgage value of the property object to False if it can be unmortgaged
        current_property = win.properties[pos]
        if current_property.mortgage:#if it has been mortgaged then it must be able to be unmortgaged
            self.money -= current_property.purchase/2 + current_property.purchase/10 #takes away half the purchase value + 10%
            current_property.mortgage = False

    def to_jail(self):#if player rolls 3 doubles in a row or lands on go to jail then they go to jail
        self.pos = 10

    def land_on_go_to_jail(self):
        if self.pos == 30: #30 is the position of the go to jail slot on the board
            self.to_jail()
            return True
        else:
            return False

    def land_on_go(self):
        if self.pos == 0:
            self.money += 200

    def land_on_free_parking(self):
        if self.pos == 20:
            return True
        else:
            return False

    def remove_assets(self, win, have_enough_money: bool):#if a player declares bankruptcy then there propertys and cash need to be removed and reset or given to the player who caused them to go bankrupt
        eliminator = win.properties[self.pos].owned#this is who owns the current property the player is on
        if have_enough_money or eliminator is None:#if the player had enough money then no other player got them out or a tax card which is owned by None could've got them out
            eliminator = None#sets the eliminator to None as it could be a player object but the player did not get them out
        else:
            eliminator.money += self.money #gives the players money to the player who got them out
        for sets in self.owned_propertys:#goes through the propertys the player owned
            for property in sets:
                property.owned = None
                self.remove_property(property)#removes the properties from their list
                property.owned = eliminator#if no-one got them out then the owned value is reset
                if eliminator is not None:
                    eliminator.add_property(property, win)#the player who got them out gets the properties
                else:
                    property.amount_houses = 0#if no-one got them out then the values that could've changed are re-set
                    property.mortgage = False


    def check_if_out(self):
        return self.out

    def return_variables(self): #this will be used to get all the information that will be sent over the server
        return self.pos,self._radius,self.colour, self.money, self.username,self.out, self.owned_propertys



class Auction:#the auction classed is used when a player lands on an unowned property but does not buy it
    def __init__(self, auction_list: list, property_pos: int, win):
        self.players = auction_list.copy()
        self.players_out = [player for player in auction_list.copy() if player.out is True]
        self.amounts = []
        self.amount = 0
        self.property = win.properties[property_pos]
        self.surface = win
        self.turn = 0
        for player_index in range(len(self.players)):#this checks whether the first player or succeding players are out and if they are then it goes through the players until someone is not out
            if self.players[player_index] not in self.players_out:
                self.turn = player_index #sets turn to first player who is not out
                break



    def draw(self):#draws a white rectangle and graphics to do with what happens in the auction
        pygame.draw.rect(self.surface, COLOURS["WHITE"], (PROPERTY_HEIGHT, PROPERTY_HEIGHT, WINDOW_WIDTH*27/64, WINDOW_WIDTH*27/64))
        self.property.enlarge_property(self.surface, 0)
        self.draw_bidding_squares()
        render_text(self.surface, font, self.players[self.turn].username, COLOURS["GREEN"], (WINDOW_WIDTH/4, SQUARE_MEASUREMENTS/2 +20))

    def draw_bidding_squares(self): #draws the squares in which it shows the previous and current bid
        for i in range(6):
            amount_boxes = (490, 90 + i* 520/ 6, 130, 520/ 6)
            x,y = pygame.Rect(amount_boxes).center
            if len(self.amounts) > i:
                render_text(self.surface, font, str(self.amounts[i]),COLOURS["BLACK"], (x,y))
                pygame.draw.rect(self.surface, self.players[(self.turn + i) % len(self.players)].colour, amount_boxes,1)

    def add_amount(self, amount):#checks if player can bid the amount they want, adds it to the amounts and moves to next player
        if self.players[self.turn].money >= (self.amount + amount):
            self.amount += amount
            self.amounts = [self.amount] + self.amounts
            self.calculate_turn()

    def leave(self):#appends player to the players_out list and then changes turn for next player
        self.players_out.append(self.players[self.turn])
        self.calculate_turn()

    def check_finished(self):#if there is only one player more in the player list than player_out list then there is only one player able to bid and thus have won the auction
        if len(self.players)-len(self.players_out) <= 1:
            return True
        else:
            return False

    def calculate_turn(self):#changes the turn value to the index of the next available player in self.players
        self.turn += 1
        self.turn %= len(self.players)
        if self.players[self.turn] in self.players_out:#if the current player is out then it can not be there turn
            self.calculate_turn()



class Deal:
    def __init__(self, player, targeted_player, win):
        self.player = player#this is the player who initiated the deal
        self.targeted_player = targeted_player#this is the player who is being dealt with
        self.money_give = 0
        self.money_get = 0
        self.propertys_give = []
        self.propertys_get = []
        self.surface = win

    def draw(self):#draws the deal information and graphics to the screen
        rect = (
            PROPERTY_HEIGHT, PROPERTY_HEIGHT, SQUARE_MEASUREMENTS - PROPERTY_HEIGHT * 2, SQUARE_MEASUREMENTS - PROPERTY_HEIGHT * 2)
        pygame.draw.rect(self.surface, COLOURS["WHITE"], rect)
        x,y = pygame.Rect(rect).midtop
        pygame.draw.line(self.surface, COLOURS["BLACK"], (x,y), (x, y + (SQUARE_MEASUREMENTS - PROPERTY_HEIGHT * 2)))
        render_text(self.surface, font, self.player.username, self.player.colour, ((x + PROPERTY_HEIGHT) / 2, y + 20))
        render_text(self.surface, font, self.targeted_player.username, self.targeted_player.colour, (x + (x - PROPERTY_HEIGHT) / 2, y + 20))
        pygame.draw.rect(self.surface, COLOURS["BLACK"], (85,550,180,40),2)
        render_text(self.surface, font, str(self.money_give), COLOURS["DARK BLUE"], (175,570))
        pygame.draw.rect(self.surface, COLOURS["BLACK"], (435,550,180,40),2)
        render_text(self.surface, font, str(self.money_get), COLOURS["DARK BLUE"], (525, 570))
        for i in range(len(self.propertys_give)):
            render_text(self.surface, font, self.propertys_give[i].name, self.propertys_give[i].colour, ((x + PROPERTY_HEIGHT) / 2, y + 50 + i * 30))
        for i in range(len(self.propertys_get)):
            render_text(self.surface, font, self.propertys_get[i].name, self.propertys_get[i].colour, (x + (x - PROPERTY_HEIGHT) / 2, y + 50 + i * 30))



    def add_propertys(self,x,y):#checks if player clicked on a property they or the player they're dealing with own
        property_give = self.player.check_owned_property(x,y)#goes through the player's properties who initiated the deal and returns the property if there mouse is on one they own
        property_get = self.targeted_player.check_owned_property(x,y)#goes through the properties of the player who is being dealed with and returns the property if the mouse is over one they own
        if property_give is not None:#if mouse was not over a property or a property they did not own then None would've been returned
            self.propertys_give.remove(property_give) if property_give in self.propertys_give else self.propertys_give.append(property_give)
        if property_get is not None:
            self.propertys_get.remove(property_get) if property_get in self.propertys_get else self.propertys_get.append(property_get)
            #if the player had already added it to property_get/give list then it is removed from the list if it is not in the list then the property is added


    def accept(self):#if the player being dealt with accepts the deal then money and properties change between the two players
        for property in self.propertys_give:#goes through the propertys in the player who is making the deal
            self.player.remove_property(property)#removes propertys from the player_owned list
            property.owned = self.targeted_player#changing the propertys_owned status to the new owner
            self.targeted_player.add_property(property, self.surface)#adding the properties to the owned_propertys list of the player who is being dealt with
        for property in self.propertys_get:#goes through the propertys the player who initiated the deal wants
            self.targeted_player.remove_property(property)
            property.owned = self.player
            self.player.add_property(property, self.surface)#the player who initiated the deal recieves the properties they wanted
        self.player.money += (self.money_get - self.money_give)#takes away and adds the money they gave and wanted repectively
        self.targeted_player.money += (self.money_give - self.money_get)

    def change_money(self, amount: str):#checks whether the amount goes to money_give or get and whether it is being added or taken away
        sign = amount[0]#this will be either a "+" or "-"
        amount = amount[1:]#this removes the sign from the amount
        if amount[-1] == " ":#if it is to do with money_get then the amount string will have an empty character at the end
            amount = amount[:-1]
            self.money_get = self.sort_signs(self.money_get, sign, amount, "get")
        else:
            self.money_give = self.sort_signs(self.money_give, sign, amount, "give")

    def sort_signs(self, player_money: int, sign: str, amount: str, get_or_give: str):
        if sign == "+":
            player_money += int(amount)#adding the amount as the sign is "+"
        else:
            player_money -= int(amount)#minusing the amount as the sign is "-"
        player_money = self.check_money_is_valid(player_money, get_or_give)
        return player_money

    def check_money_is_valid(self, player_money, get_or_give):#this will check whether the amount is below 0 or greater than the amount
        maximum_money = self.targeted_player.money if get_or_give == "get" else self.player.money#checks which player the money will be given from
        if player_money<0:#the money can not go below zero
            player_money = 0
        elif player_money> maximum_money:#the player can not put up more money than they have
            player_money = maximum_money
        return player_money #if the player_money was between 0 and the maximum money then that amount will be returned