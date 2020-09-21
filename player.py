import pygame
from constants import *
pygame.font.init()
font = pygame.font.SysFont('arial', 26)


#the player class primarily will include decisions that relate to the player for instance when buying a property, although it involves the board it is primarily affected by the player


class Player:
    def __init__(self, pos, radius, colour, username):
        self.pos = pos
        self.radius = radius
        self.colour = colour
        self.money = starting_money
        self.username = username
        self.owned_propertys = []
        #add list which uses the thing to add propertys to create the list with every set

    def check_they_can_pay(self, figure):
        if self.money - figure > 0:
            return True
        else:
            return False



    def draw(self, win):
        space = win.properties[self.pos]
        x, y = pygame.Rect(space.x, space.y, space.get_rect().w, space.get_rect().h).center
        pygame.draw.circle(win, self.colour, (x, y), self.radius)
        pygame.draw.circle(win, COLOURS["BLACK"], (x,y), self.radius,1)

    def draw_player_square(self,win, x, variable, width, height,turn):
        squ = (x, variable*height , width, height)
        pygame.draw.rect(win, COLOURS["GREEN"], squ, 5) if turn== variable else None
        pygame.draw.rect(win, COLOURS["BLACK"], (squ),1)
        render_text(win, font, self.username, self.colour, (pygame.Rect(squ).centerx- width/4, pygame.Rect(squ).centery -height/4))
        render_text(win, font, str(int(self.money)), COLOURS["BLACK"], (pygame.Rect(squ).centerx, pygame.Rect(squ).centery - height/4))
        set_dist = 0
        for sets in self.owned_propertys:
            set_dist +=1
            prop_dist = 0
            for p in sets:
                pygame.draw.rect(win, p.colour, (pygame.Rect(squ).midleft[0] + set_dist *25, pygame.Rect(squ).midleft[1] + prop_dist* 25, 20, 20))
                pygame.draw.rect(win, COLOURS["BLACK"], (pygame.Rect(squ).midleft[0] + set_dist*25, pygame.Rect(squ).midleft[1] + prop_dist*25, 20, 20),1)
                prop_dist +=1

    def property_action(self, win):
        action = win.properties[self.pos].property_actions(self)
        return action


    def move(self, amount):
        if self.pos + amount > 39:
            self.pos = (self.pos + amount) - 40
        else:
            self.pos += amount

    def pass_go(self, roll_no):
        if self.pos - roll_no < 0:
            self.money += 200

    def add_property(self, property, win):
        added = False
        for set in self.owned_propertys:
            for p in set:
                if p.colour == property.colour:
                    set.append(property)
                    added = True
                    property.full_set = self.check_for_full_set(win, len(set))
                    break  # this will check through the propertys owned and if the colour is the same then it will append it into the list otherwise it'll just add it
        if added == False:
            self.owned_propertys.append([property])
            self.owned_propertys.sort(key= lambda x: win.properties.index(x[0]))

    def find_position(self, win, elem):
        return win.properties.index(elem[0])


    def check_for_full_set(self, win, set_length):
        if len(win.sorted_sets[list(COLOURS.keys())[list(COLOURS.values()).index(win.properties[self.pos].colour)]]) == set_length:

            return True
        else:
            return False

    def check_owned_property(self):
        x,y = pygame.mouse.get_pos()
        for sets in self.owned_propertys:
            for p in sets:
                if pygame.Rect(p.x, p.y, p.width, p.height).collidepoint(x,y):
                    return p





    def buy_property(self, win, other_player = None, amount = None):
        #when this is but into the main function the win will become the instance of the board class so the player and board can work in unison
        space = win.properties[self.pos if other_player == None else other_player.pos]
        amount = space.purchase if amount == None else amount
        if self.check_they_can_pay(amount):
            self.money -= amount
            self.add_property(space,win)
            space.owned = self
            return True

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
                return True
            #create function that will identify utility card and then x by dice roll

    def pay_tax(self, win):
        space = win.properties[self.pos]
        rent = space.rent
        self.money -= rent

    def add_house(self, win, pos):
        current_property = win.properties[pos]
        if current_property.full_set:
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
        if current_property.mortgage == False:
            self.money += current_property.purchase/2
            current_property.mortgage = True

    def unmortgage(self, win, pos):
        current_property = win.properties[pos]
        if current_property.mortgage:
            self.money -= current_property.purchase/2 + current_property.purchase/10
            current_property.mortgage = False












class Auction:
    def __init__(self, auction_list, property, win):
        self.players = auction_list.copy()
        self.amounts = []
        self.amount = 0
        self.property = property
        self.surface = win
        self.turn = 0

    def draw(self):
        pygame.draw.rect(self.surface, COLOURS["WHITE"], (
            PROPERTY_HEIGHT, PROPERTY_HEIGHT, BOARD_WIDTH - PROPERTY_HEIGHT * 2, BOARD_WIDTH - PROPERTY_HEIGHT * 2))
        self.property.enlarge_property(self.surface, 0)
        for i in range(6):
            amount_boxes = (490, 90 + i* 520/ 6, 130, 520/ 6)
            x,y = pygame.Rect(amount_boxes).center
            if len(self.amounts) > i:
                render_text(self.surface, font, str(self.amounts[i]),COLOURS["BLACK"], (x,y))
                pygame.draw.rect(self.surface, self.players[(self.turn + i) % len(self.players)].colour, amount_boxes,
                                 1)
        render_text(self.surface, font, self.players[self.turn].username, COLOURS["GREEN"], (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))

    def add_amount(self, amount):
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
            PROPERTY_HEIGHT, PROPERTY_HEIGHT, BOARD_WIDTH - PROPERTY_HEIGHT * 2, BOARD_WIDTH - PROPERTY_HEIGHT * 2)
        pygame.draw.rect(self.surface, COLOURS["WHITE"], rect)
        x,y = pygame.Rect(rect).midtop
        pygame.draw.line(self.surface,COLOURS["BLACK"], (x,y), (x, y + (BOARD_WIDTH - PROPERTY_HEIGHT *2)))
        render_text(self.surface, font, self.player.username, self.player.colour, ((x + PROPERTY_HEIGHT)/2, y +20))
        render_text(self.surface, font, self.targeted_player.username, self.targeted_player.colour, (x + (x-PROPERTY_HEIGHT)/2, y +20))
        print(len(self.propertys_give))
        if len(self.propertys_give) != 0:
            for i in range(len(self.propertys_give)):
                render_text(self.surface, font, self.propertys_give[i].name, self.propertys_give[i].colour, ((x + PROPERTY_HEIGHT)/2, y +40 +i*20))

    def add_propertys(self):
        property = self.player.check_owned_property()
        if property != None:
            self.propertys_give.remove(property) if property in self.propertys_give else self.propertys_give.append(property)
            self.propertys_get.remove(property) if property in self.propertys_get else self.propertys_give.append(property)








