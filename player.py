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

    def sort_sets(self, win):
        self.owned_propertys = win.sorted_sets
        self.owned_propertys = [[None for j in i] for i in self.owned_propertys]

    def draw(self, win):
        space = win.properties[self.pos]
        x, y = pygame.Rect(space.x, space.y, space.get_rect().w, space.get_rect().h).center
        pygame.draw.circle(win, self.colour, (x, y), self.radius)

    def draw_player_square(self,win, x, variable, width, height):
        squ = (x, variable*height , width, height)
        pygame.draw.rect(win, BLACK, (squ),1)
        render_text(win, font, self.username, BLACK, (pygame.Rect(squ).centerx, pygame.Rect(squ).centery -height/4))
        render_text(win, font, str(self.money), BLACK, (pygame.Rect(squ).center))

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

    def add_property(self, property):
        added = False
        for l in self.owned_propertys:
            for p in l:
                if p.colour == property.colour:
                    l.append(property)
                    added = True
                    break#this will check through the propertys owned and if the colour is the same then it will append it into the list otherwise it'll just add it
        if added == False:
            self.owned_propertys.append([property])






    def buy_property(self, win):
        #when this is but into the main function the win will become the instance of the board class so the player and board can work in unison
        space = win.properties[self.pos]
        self.money -= space.purchase
        self.add_property(space)
        space.owned = self

    def pay_rent(self, win):
        #this will be used to player who owns the property that the current player has landed on.
        space = win.properties[self.pos]
        rent = space.rent[str(space.amount_houses)]
        self.money -= rent
        space.owned.money += rent







