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



    def draw(self, win):
        space = win.properties[self.pos]
        x, y = pygame.Rect(space.x, space.y, space.get_rect().w, space.get_rect().h).center
        pygame.draw.circle(win, self.colour, (x, y), self.radius)
        pygame.draw.circle(win, COLOURS["BLACK"], (x,y), self.radius)

    def draw_player_square(self,win, x, variable, width, height):
        squ = (x, variable*height , width, height)
        pygame.draw.rect(win, COLOURS["BLACK"], (squ),1)
        render_text(win, font, self.username, COLOURS["BLACK"], (pygame.Rect(squ).centerx, pygame.Rect(squ).centery -height/4))
        render_text(win, font, str(self.money), COLOURS["BLACK"], (pygame.Rect(squ).center))

    def property_action(self, win):
        action = win.properties[self.pos].property_actions()
        return action


    def move(self, amount):
        if self.pos + amount > 39:
            self.pos = (self.pos + amount) - 40
        else:
            self.pos += amount

    def pass_go(self, roll_no):
        if self.pos - roll_no < 0:
            self.money += 200

    def add_property(self, property, board):
        added = False
        for set in self.owned_propertys:
            for p in set:
                if p.colour == property.colour:
                    set.append(property)
                    added = True
                    property.full_set = self.check_for_full_set(board, len(set))
                    break#this will check through the propertys owned and if the colour is the same then it will append it into the list otherwise it'll just add it
        if added == False:
            self.owned_propertys.append([property])

    def check_for_full_set(self, win, set_length):
        print(len(win.sorted_sets[list(COLOURS.keys())[list(COLOURS.values()).index(win.properties[self.pos].colour)]]))
        print(set_length)
        if len(win.sorted_sets[list(COLOURS.keys())[list(COLOURS.values()).index(win.properties[self.pos].colour)]]) == set_length:
            return True
        else:
            return False




    def buy_property(self, win):
        #when this is but into the main function the win will become the instance of the board class so the player and board can work in unison
        space = win.properties[self.pos]
        self.money -= space.purchase
        self.add_property(space,win)
        space.owned = self

    def pay_rent(self, win):
        #this will be used to player who owns the property that the current player has landed on and tax that the player lands on
        space = win.properties[self.pos]
        rent = space.rent[str(space.amount_houses)]
        if win.properties[self.pos].full_set == True:
            rent *= 2
        self.money -= rent
        space.owned.money += rent

    def pay_tax(self, win):
        space = win.properties[self.pos]
        rent = space.rent
        self.money -= rent

    def auction(self, win, amount):
         pass
         #auction_amount += amount
         #could make this into a class









