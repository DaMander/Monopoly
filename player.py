from constants import *
pygame.font.init()
font = pygame.font.SysFont('arial', 26)


#the player class primarily will include decisions that relate to the player for instance when buying a property, although it involves the board it is primarily affected by the player


class Player:
    def __init__(self, pos, radius, colour, money, username, out, propertys ):
        self.pos = pos
        self.radius = radius
        self.colour = colour
        self.money = money
        self.username = username
        self.out = out
        self.owned_propertys = propertys

        #add list which uses the thing to add propertys to create the list with every set

    def check_they_can_pay(self, figure):
        if self.money - figure >= 0:
            return True
        else:
            return False



    def draw(self, win):
        space = win.properties[self.pos]
        x, y = pygame.Rect(space.x, space.y, space.get_rect().w, space.get_rect().h).center
        pygame.draw.circle(win, self.colour, (x, y), self.radius)
        pygame.draw.circle(win, COLOURS["BLACK"], (x,y), self.radius,1)

    def draw_player_square(self, win, player_index, height, turn):
        player_square = (SQUARE_MEASUREMENTS, player_index * height, WINDOW_WIDTH*29/64, height)
        self.draw_player_name_and_money(win, player_square, player_index, height, turn)
        self.draw_player_propertys(win, player_square, player_index, height)


    def draw_player_name_and_money(self,win,player_square,player_index,height, turn):
        pygame.draw.rect(win, COLOURS["GREEN"], player_square, 5) if turn == player_index else None
        pygame.draw.rect(win, COLOURS["BLACK"], player_square, 1)
        x,y = pygame.Rect(player_square).center
        render_text(win, font, self.username, self.colour,(x - WINDOW_WIDTH * 29 / 256, y - height / 4))
        render_text(win, font, str(int(self.money)), COLOURS["BLACK"],(x, y - height / 4))

    def draw_player_propertys(self, win, player_square, player_index, height):
        set_dist = 0
        for sets in self.owned_propertys:
            set_dist += 1
            prop_dist = 0
            for p in sets:
                x,y = pygame.Rect(player_square).midleft
                pygame.draw.rect(win, p.colour, (x + set_dist * WINDOW_WIDTH*5/256,y + prop_dist * WINDOW_WIDTH*5/256, WINDOW_WIDTH*1/64, WINDOW_WIDTH*1/64))
                pygame.draw.rect(win, COLOURS["BLACK"], (x + set_dist * WINDOW_WIDTH*5/256,y + prop_dist * WINDOW_WIDTH*5/256, WINDOW_WIDTH*1/64, WINDOW_WIDTH*1/64), 1)
                prop_dist += 1
        if self.out:
            pygame.draw.line(win, COLOURS["RED"], (SQUARE_MEASUREMENTS, player_index * height), (SQUARE_MEASUREMENTS + WINDOW_WIDTH * 29 / 64, player_index * height + height), 5)

    def check_rect(self, rect):
        x,y = pygame.mouse.get_pos()
        return pygame.Rect(rect).collidepoint(x,y)

    def property_action(self, win):
        action = win.properties[self.pos].property_actions(self)
        return action


    def move(self, amount):
        if self.pos + amount > 39:
            self.pos = (self.pos + amount) - 40
            self.pass_go()
        else:
            self.pos += amount

    def pass_go(self):
        self.money += 200

    def add_property(self, property, win):
        added = False
        for set in self.owned_propertys:
            for p in set:
                if p.colour == property.colour:
                    set.append(property)
                    added = True
                    if self.check_for_full_set(win, len(set)):
                        for prop_full_set in set:
                            prop_full_set.full_set = True
                    break  # this will check through the propertys owned and if the colour is the same then it will append it into the list otherwise it'll just add it
        if added is False:
            self.owned_propertys.append([property])
            self.owned_propertys.sort(key= lambda x: win.properties.index(x[0]))

    def remove_property(self, property):
        for set in self.owned_propertys:
            if property in set:
                set.remove(property)
                break
        self.owned_propertys = [i for i in self.owned_propertys if i]




    def check_for_full_set(self, win, set_length):
        if len(win.SORTED_SETS[list(COLOURS.keys())[list(COLOURS.values()).index(win.properties[self.pos].colour)]]) == set_length:
            return True
        else:
            return False

    def check_owned_property(self,x,y):
        for sets in self.owned_propertys:
            for p in sets:
                if pygame.Rect(p.x, p.y, p.width, p.height).collidepoint(x,y):
                    return p





    def buy_property(self, win, other_player = None, amount = None):
        #when this is but into the main function the win will become the instance of the board class so the player and board can work in unison
        space = win.properties[self.pos if other_player is None else other_player.pos]
        amount = space.purchase if amount is None else amount
        if self.check_they_can_pay(amount):
            self.money -= amount
            self.add_property(space,win)
            space.owned = self
            return True
        else:
            print("insufficient funds") #needs to be function where they can use 'make deals' and 'look at propertys' to gain the cash they need, so it goes to sction taken 1 but they can't click end turn, could have back button when there finished which then executes payment

    def pay_rent(self, win):
        #this will be used to player who owns the property that the current player has landed on and tax that the player lands on
        space = win.properties[self.pos]
        if space.owned != self and space.mortgage != True:
            rent = space.rent[str(space.amount_houses)]
            if space.full_set == True and space.amount_houses == 0:
                rent *= 2
            if self.check_they_can_pay(rent):
                self.money -= rent
                space.owned.money += rent
                return True, 0
            else:
                return False, rent
            #create function that will identify utility card and then x by dice roll

    def pay_tax(self, win):
        space = win.properties[self.pos]
        rent = space.rent
        if self.check_they_can_pay(rent):
            rent = space.rent
            self.money -= rent
            return True, 0
        else:
            return False, rent

    def add_house(self, win, pos):
        current_property = win.properties[pos]
        if current_property.full_set and not current_property.mortgage and self.money - current_property.houses_price >=0:
            if current_property.amount_houses < 5:
                self.money -= current_property.houses_price
                current_property.amount_houses += 1

    def remove_house(self, win, pos):
        current_property = win.properties[pos]
        if current_property.full_set:
            if current_property.amount_houses > 0:
                self.money += current_property.houses_price/2
                current_property.amount_houses -= 1

    def mortgage(self, win, pos):
        current_property = win.properties[pos]
        if not current_property.mortgage and (current_property.amount_houses == 0 or current_property.houses_price is None):#if it has no houses then it can be mortgage and if it has no house price it means it's a station or utility
            self.money += current_property.purchase/2
            current_property.mortgage = True

    def unmortgage(self, win, pos):
        current_property = win.properties[pos]
        if current_property.mortgage:
            self.money -= current_property.purchase/2 + current_property.purchase/10
            current_property.mortgage = False

    def to_jail(self):
        self.pos = 10

    def land_on_go_to_jail(self, win):
        if self.pos == 30:
            self.to_jail()
            return True

    def remove_assets(self, win, have_enough_money):
        if have_enough_money:
            eliminator = None
        else:
            eliminator = win.properties[self.pos].owned
            eliminator.money += self.money
        for sets in self.owned_propertys:
            for property in sets:
                self.remove_property(property)
                property.owned = eliminator
                if eliminator is not None:
                    eliminator.add_property(property, win)

    def check_if_out(self):
        return self.out

    def return_variables(self):
        return self.pos,self.radius,self.colour, self.money, self.username,self.out, self.owned_propertys


def check_rect(rect):
    x,y = pygame.mouse.get_pos()
    return pygame.Rect(rect).collidepoint(x,y)


class Auction:
    def __init__(self, auction_list, property_pos, win):
        self.players = auction_list.copy()
        self.amounts = []
        self.amount = 0
        self.property = win.properties[property_pos]
        self.surface = win
        self.turn = 0

    def draw(self):
        pygame.draw.rect(self.surface, COLOURS["WHITE"], (PROPERTY_HEIGHT, PROPERTY_HEIGHT, WINDOW_WIDTH*27/64, WINDOW_WIDTH*27/64))
        self.property.enlarge_property(self.surface, 0)
        self.draw_bidding_squares()
        render_text(self.surface, font, self.players[self.turn].username, COLOURS["GREEN"], (WINDOW_WIDTH/4, SQUARE_MEASUREMENTS/2 +20))

    def draw_bidding_squares(self):
        for i in range(6):
            amount_boxes = (490, 90 + i* 520/ 6, 130, 520/ 6)
            x,y = pygame.Rect(amount_boxes).center
            if len(self.amounts) > i:
                render_text(self.surface, font, str(self.amounts[i]),COLOURS["BLACK"], (x,y))
                pygame.draw.rect(self.surface, self.players[(self.turn + i) % len(self.players)].colour, amount_boxes,
                                 1)

    def add_amount(self, amount):
        if self.players[self.turn].money >= (self.amount + amount):
            self.amount += amount
            self.amounts = [self.amount] + self.amounts
            self.turn += 1
            self.turn %= len(self.players)

    def leave(self):
        self.players.pop(self.turn)
        self.turn %= len(self.players)

    def check_finished(self):
        if len(self.players) == 1:
            return True

class Deal:
    def __init__(self, player, targeted_player, win):
        self.player = player
        self.targeted_player = targeted_player
        self.money_give = 0
        self.money_get = 0
        self.propertys_give = []
        self.propertys_get = []
        self.surface = win

    def draw(self):
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



    def add_propertys(self,x,y):
        property_give = self.player.check_owned_property(x,y)
        property_get = self.targeted_player.check_owned_property(x,y)
        if property_give != None :
            self.propertys_give.remove(property_give) if property_give in self.propertys_give else self.propertys_give.append(property_give)
        if property_get != None:
            self.propertys_get.remove(property_get) if property_get in self.propertys_get else self.propertys_get.append(property_get)


    def accept(self):
        for property in self.propertys_give:
            self.player.remove_property(property)
            property.owned = self.targeted_player
            self.targeted_player.add_property(property, self.surface)
        for property in self.propertys_get:
            self.targeted_player.remove_property(property)
            property.owned = self.player
            self.player.add_property(property, self.surface)
        self.player.money += (self.money_get - self.money_give)
        self.targeted_player.money += (self.money_give - self.money_get)

    def change_money(self, amount):
        sign = amount[0]
        amount = amount[1:]
        if amount[-1] == " ":
            amount = amount[:-1]
            self.money_get = self.sort_signs(self.money_get, sign, amount, "get")
        else:
            self.money_give = self.sort_signs(self.money_give, sign, amount, "give")

    def sort_signs(self, player_money, sign, amount, get_or_give):
        if sign == "+":
            player_money += int(amount)
        else:
            player_money -= int(amount)
        player_money = self.check_money_is_valid(player_money, get_or_give)
        return player_money

    def check_money_is_valid(self, player_money, get_or_give):#this will check whether the amount is below 0 or greater than the amount
        maximum_money = self.targeted_player.money if get_or_give == "get" else self.player.money
        if player_money<0:                       #the player has as this would be unfair and negatively affect the gameplay
            player_money = 0
        elif player_money> maximum_money:
            player_money = maximum_money
        return player_money