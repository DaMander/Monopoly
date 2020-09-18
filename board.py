import random

import pygame
import json
from constants import *
from community_chest_and_chance import *
pygame.init()


"""the board document will primarily deal with the graphics side of the gamne, drawing the board and items when a command is executed"""


class Board(pygame.Surface):   #this class creates the 40 instances of the location class needed fot the 40 propertys in monopoly
    def __init__(self, width, height):
        super().__init__((width, height))
        self.cards = []
        self.properties = []
        self.sorted_sets = {
            "BROWN": [],
            "LIGHT BLUE": [],
            "PINK": [],
            "ORANGE": [],
            "RED": [],
            "YELLOW": [],
            "GREEN": [],
            "DARK BLUE": [],
            "BLACK": [],
            "BOARD COLOUR": []
        }
#this could probably be shortened somehow
        starting_value = BOARD_WIDTH-PROPERTY_HEIGHT
        self.properties.append(Property("corner", starting_value, starting_value, *file[str(len(self.properties))].values()))
        for i in range(9):
            self.properties.append(Property( "vert", (starting_value-PROPERTY_WIDTH) - (i * PROPERTY_WIDTH), starting_value, *file[str(len(self.properties))].values()))
        self.properties.append(Property("corner", 0, starting_value, *file[str(len(self.properties))].values()))
        for i in range(9):
            self.properties.append(Property("hori", 0, (starting_value-PROPERTY_WIDTH) - (i * PROPERTY_WIDTH), *file[str(len(self.properties))].values()))

        self.properties.append(Property("corner", 0,0, *file[str(len(self.properties))].values()))
        for i in range(9):
            self.properties.append(Property("vert", PROPERTY_HEIGHT + (i * PROPERTY_WIDTH), 0, *file[str(len(self.properties))].values()))

        self.properties.append(Property("corner", BOARD_WIDTH-PROPERTY_HEIGHT, 0, *file[str(len(self.properties))].values()))
        for i in range(9):
            self.properties.append(Property("hori", BOARD_WIDTH-PROPERTY_HEIGHT, PROPERTY_HEIGHT + (i * PROPERTY_WIDTH), *file[str(len(self.properties))].values()))
        for i in range(len(comm_cards)):
            self.cards.append(Card(*comm_cards[str(len(self.cards))].values()))



        self.buttons = [[Button("ROLL DICE", BOARD_WIDTH/2, WINDOW_HEIGHT/2, COLOURS["GREEN"], True)],

                        [Button("END TURN", BOARD_WIDTH/2, WINDOW_HEIGHT/2, COLOURS["RED"], True),
                         Button("MAKE DEAL", BOARD_WIDTH/2, 150 + WINDOW_HEIGHT/2, COLOURS["PINK"], True),
                         Button("LOOK AT PROPERTYS", BOARD_WIDTH/2,  WINDOW_HEIGHT/2 -150, COLOURS["YELLOW"], True)],

                        [Button("PURCHASE", PROPERTY_HEIGHT + PROPERTY_WIDTH + 120, 9 * PROPERTY_WIDTH +10, COLOURS["GREEN"], True),
                         Button("AUCTION", PROPERTY_HEIGHT + PROPERTY_WIDTH + 270, 9 * PROPERTY_WIDTH +10, COLOURS["DARK BLUE"], True)],

                        [#Button("ACCEPT", PROPERTY_HEIGHT +10, PROPERTY_HEIGHT+ 7*PROPERTY_WIDTH, COLOURS["GREEN"],False, PROPERTY_ENLARGE_WIDTH/3),
                         #Button("COUNTER", PROPERTY_HEIGHT+10+PROPERTY_ENLARGE_WIDTH/3, PROPERTY_HEIGHT+ 7*PROPERTY_WIDTH, COLOURS["ORANGE"], False, PROPERTY_ENLARGE_WIDTH/3),
                         #Button("REJECT", PROPERTY_HEIGHT + 10 + 2 * PROPERTY_ENLARGE_WIDTH / 3,PROPERTY_HEIGHT + 7 * PROPERTY_WIDTH, COLOURS["RED"], False,PROPERTY_ENLARGE_WIDTH / 3)
                         ],#making a deal

                        [Button("+ HOUSE", PROPERTY_HEIGHT + PROPERTY_WIDTH +10, PROPERTY_HEIGHT + 7*PROPERTY_WIDTH, COLOURS["GREEN"], False, PROPERTY_ENLARGE_WIDTH/2, 50),
                         Button("- HOUSE", PROPERTY_HEIGHT + PROPERTY_WIDTH +10, PROPERTY_HEIGHT + 7*PROPERTY_WIDTH +50, COLOURS["RED"], False, PROPERTY_ENLARGE_WIDTH/2, 50),
                         Button("MORTGAGE", PROPERTY_HEIGHT + PROPERTY_WIDTH +PROPERTY_ENLARGE_WIDTH/2 +10, PROPERTY_HEIGHT + 7*PROPERTY_WIDTH, COLOURS["GREEN"], False, PROPERTY_ENLARGE_WIDTH/2, 50),
                         Button("UNMORTGAGE", PROPERTY_HEIGHT + PROPERTY_WIDTH +10 + PROPERTY_ENLARGE_WIDTH/2, PROPERTY_HEIGHT + 7*PROPERTY_WIDTH +50, COLOURS["RED"], False, PROPERTY_ENLARGE_WIDTH/2, 50),
                         Button("BACK", PROPERTY_HEIGHT+ PROPERTY_WIDTH + 10, PROPERTY_HEIGHT, COLOURS["RED"], False, PROPERTY_HEIGHT, PROPERTY_WIDTH/2)],#player property actions - mortgage, buy houses etc.

                        [Button("BID 100", PROPERTY_HEIGHT +10, PROPERTY_HEIGHT+ 7*PROPERTY_WIDTH, COLOURS["RED"],False, PROPERTY_ENLARGE_WIDTH/3),
                         Button("BID 10", PROPERTY_HEIGHT+10+PROPERTY_ENLARGE_WIDTH/3, PROPERTY_HEIGHT+ 7*PROPERTY_WIDTH, COLOURS["ORANGE"], False, PROPERTY_ENLARGE_WIDTH/3),
                         Button("BID 1", PROPERTY_HEIGHT +10 +2*PROPERTY_ENLARGE_WIDTH/3, PROPERTY_HEIGHT+ 7*PROPERTY_WIDTH, COLOURS["PINK"], False, PROPERTY_ENLARGE_WIDTH/3),#auction
                         Button("LEAVE", PROPERTY_HEIGHT+ PROPERTY_WIDTH + 10, PROPERTY_HEIGHT, COLOURS["RED"], False, 2*PROPERTY_HEIGHT, PROPERTY_WIDTH/2)]
                        ]

        self.always_button = Button("BANK", WINDOW_WIDTH-150,0,COLOURS["RED"], False) #this button will be used for the player to delcare bankruptcy

    def sort_sets(self):
        for p in self.properties:
            if p.purchase != None:
                self.sorted_sets[list(COLOURS.keys())[list(COLOURS.values()).index(p.colour)]].append(p)





    def draw_background(self, list_of_players, turn):
        self.fill((200, 200, 255))
        for p in self.properties:
            p.draw_propertys(self) #this goes through all the propertys and draws them to the board
        for i in range(len(list_of_players)):
            list_of_players[i].draw_player_square(self, BOARD_WIDTH, i, WINDOW_WIDTH-BOARD_WIDTH, WINDOW_HEIGHT/len(list_of_players),turn) #this will draw the rectangles on the right which store player info


    def draw_onto_board(self,player_pos, action_taken, other_card):
        self.draw_action(action_taken, player_pos, other_card) #this will draw graphics on the screen depending on what happens

        self.always_button.draw(self) #this will draw buttons that are always on the screen

        if action_taken <6: #this draws the buttons to the screen depending on what happens
            for b in self.buttons[action_taken]:
                b.draw(self)

            #this will draw all the propertys onto the board using the draw function in the Property class



    def draw_action(self, action_taken, player_pos, other_card):
        pos = player_pos if other_card == None else other_card
        current_property = self.properties[pos]
        if action_taken == 2 or action_taken == 4 or action_taken == 6:
            current_property.enlarge_property(self,1) #this draws the enlarged property card to the screen
            if action_taken == 6:
                n = 2 if current_property.full_set == True and current_property.amount_houses == 0 else 1
                render_text(self, font,f'{current_property.owned.username} owns this property you paid {n*current_property.rent[str(current_property.amount_houses)]}'
                            , COLOURS["BLACK"], (PROPERTY_HEIGHT + PROPERTY_WIDTH + 120, 9 * PROPERTY_WIDTH +10))






        elif action_taken == 7 or action_taken == 8:
            current_property.enlarge_card(self)
            """if action_taken == 8:
                x = random.randint(0,len(self.cards)-1)
                render_text(self, font, f'{self.cards[x].text}', COLOURS["BLACK"],(300,300))"""




    def enlarge_property(self):
        for p in self.properties:
            if p.check_for_click_prop():
                if p.purchase != None:
                    p.enlarge_property(self,1)
                    return self.properties.index(p)
                elif p.height != p.width :
                    p.enlarge_card(self)

    def check_for_button_click(self, which_buttons):
        if which_buttons < 6:
            for b in self.buttons[which_buttons]:
                if b.check_for_press():
                    return b.text


    def utility_station_rent(self, colour):
        owned_players = []
        for p in self.sorted_sets[colour]:
            owned_players.append(p.owned)
        counts = [[x, owned_players.count(x)] for x in set(owned_players)]
        for i in range(len(counts)):
            if counts[i][0] != None:
                for p in self.sorted_sets[colour]:
                    if p.owned == counts[i][0]:
                        p.amount_houses = counts[i][1] -1











class Property(pygame.Surface): #this class is used when drawing the squares to the board, used in the Board class to allow all the instances of location to be added to a list
    def __init__(self, orientation, x, y, name, purchase = None, rent = None, houses_price = None, colour = "BOARD COLOUR"):
        super().__init__((PROPERTY_WIDTH, PROPERTY_HEIGHT))
        self.width = PROPERTY_WIDTH if orientation == "vert" else PROPERTY_HEIGHT
        self.height = PROPERTY_WIDTH if orientation == "hori" else PROPERTY_HEIGHT
        self.x = x
        self.y = y
        self.name = name
        self.purchase = purchase
        self.rent = rent
        self.mortgage = False
        self.houses_price = houses_price
        self.colour = COLOURS[colour]
        self.owned = None
        self.amount_houses = 0
        self.full_set = False
        #COLOUR



    def draw_propertys(self, win):
        self.fill((200, 200, 255))
        n = (self.x, self.y, self.width / 4, self.height) if self.width > self.height else (self.x, self.y, self.width, self.height / 4)
        pygame.draw.rect(win, self.colour, (n))
        if self.owned != None:
            pygame.draw.rect(win,self.owned.colour,(self.x, self.y, self.width, self.height),5) #this will draw the players icon on the property to show who owns it
        pygame.draw.rect(win, COLOURS["BLACK"], (self.x, self.y, self.width, self.height), 1)
        if self.houses_price != None:
            if self.amount_houses > 4:
                    pygame.draw.rect(win, COLOURS["RED"], (self.x+ 20, self.y +40, 10, 10))
            else:
                for i in range(self.amount_houses):
                    pygame.draw.rect(win, COLOURS["GREEN"], (i*15 + self.x, self.y +40, 10, 10))
        if self.mortgage:
            pygame.draw.line(win, COLOURS["RED"], (self.x, self.y), (self.x + self.width, self.y + self.height))
    """create a function which manages the text so it fits within the property space"""

    def property_actions(self, player):
        if self.purchase != None and self.owned == None: #this means it's an unowned property card
            return 2
        elif self.purchase != None and self.owned != None and self.owned != player and self.mortgage == False:#this means it's an owned property
            return 6
        elif self.purchase == None and self.rent != None:#this means it is a tax card
            return 7
        elif self.name == "COMMUNITY CHEST":
            return 8
        elif self.name == "CHANCE":
            return 1
        else:
            return 1







    def check_for_click_prop(self):
        x, y = pygame.mouse.get_pos()
        if pygame.Rect(self.x,self.y,self.width,self.height).collidepoint(x,y):
            return True

    def enlarge_property(self, win, pos):#this is graphically used to show a card which can be purchased onto the board
        n = PROPERTY_HEIGHT + PROPERTY_WIDTH * pos  # if pos = 0 the property is on the left, 1 makes the property in the middle and 2 will put it on the right
        pygame.draw.rect(win, COLOURS["WHITE"], (n, PROPERTY_HEIGHT, 7 * PROPERTY_WIDTH, 9 * PROPERTY_WIDTH))
        figures = 1 / 6 * PROPERTY_WIDTH
        pygame.draw.rect(win, COLOURS["BLACK"], (
        n + figures, PROPERTY_HEIGHT + figures, 7 * PROPERTY_WIDTH - 2 * figures, 9 * PROPERTY_WIDTH - 2 * figures), 1)
        colour_box = (n + 2 * figures, PROPERTY_HEIGHT + 2 * figures, 7 * PROPERTY_WIDTH - 4 * figures,
                      2 * PROPERTY_WIDTH - 4 * figures)
        x, y = pygame.Rect(colour_box).center
        if self.houses_price != None:
            pygame.draw.rect(win, self.colour, colour_box)
            render_text(win, font, self.name, COLOURS["BLACK"], (x, y))
            for i in range(len(self.rent)):
                render_text(win, font, f'Rent with {str(i)} house {self.rent[str(i)]}', COLOURS["BLACK"],
                            (x, y + PROPERTY_WIDTH + i * PROPERTY_WIDTH / 2))
            render_text(win, font, f'Mortgage value {int(self.purchase/2)}', COLOURS["BLACK"], (x, y + 9 * PROPERTY_WIDTH/2))
            render_text(win, font, f'Houses cost {self.houses_price} each', COLOURS["BLACK"],
                        (x, y + 5 * PROPERTY_WIDTH))
            render_text(win, font, f'Hotels, {self.houses_price} each plus 4 houses', COLOURS["BLACK"],
                        (x, y + 11 * PROPERTY_WIDTH/2))
        else:
            # draw the stations
            render_text(win, font, f'{self.name}', COLOURS["BLACK"], (x, y))
            if len(self.rent) > 2:
                for i in range(len(self.rent)):
                    render_text(win, font, f'Rent with {str(i + 1)} stations {self.rent[str(i)]}', COLOURS["BLACK"],
                                (x, y + 2 * PROPERTY_WIDTH + i * PROPERTY_WIDTH / 2))
                render_text(win, font, f'MORTGAGE VALUE - {int(self.purchase/2)}', COLOURS["BLACK"],
                            (x, y + 5 * PROPERTY_WIDTH))
            else:
                # draw the utilitys
                for i in range(len(self.rent)):
                    render_text(win, font,
                                f'If {str(i + 1)} "utility" is owned rent is {self.rent[str(i)]} times amount shown on dice',
                                COLOURS["BLACK"], (x, y + 4 * PROPERTY_WIDTH + i * PROPERTY_WIDTH / 2))

    def enlarge_card(self, win):
        pygame.draw.rect(win, COLOURS["WHITE"], (PROPERTY_HEIGHT, PROPERTY_HEIGHT + PROPERTY_WIDTH, 9*PROPERTY_WIDTH, 7*PROPERTY_WIDTH))
        line = (PROPERTY_HEIGHT, PROPERTY_HEIGHT + PROPERTY_WIDTH, 9 * PROPERTY_WIDTH, 7 * PROPERTY_WIDTH)
        pygame.draw.rect(win, COLOURS["BLACK"], line,1)
        x,y = pygame.Rect(line).center
        render_text(win,font, f'{self.name}', COLOURS["ORANGE"], (x,y))
        if self.rent != None: #this means they have landed on a tax card and I can use the center co-ordinates instead of re-doing them in the draw_action function
            render_text(win, font, f'You owe {self.rent}', COLOURS["RED"], (x,y + PROPERTY_WIDTH))

class Button:
    def __init__(self, text, x, y, color, centre, width =WINDOW_WIDTH*15/128, height = WINDOW_WIDTH*5/64):
        self.text = text
        self.color = color
        self.width = width
        self.height = height
        self.x = x - self.width / 2 if centre == True else x
        self.y = y - self.height / 2 if centre == True else y

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(win, COLOURS["BLACK"], (self.x, self.y, self.width, self.height),1)
        font = pygame.font.SysFont("comicsans", int(WINDOW_WIDTH*1/32))
        text = font.render(self.text, 1, (255,255,255))
        win.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2)))

    def check_for_press(self):
        x,y = pygame.mouse.get_pos()
        if pygame.Rect(self.x,self.y, self.width, self.height).collidepoint(x,y):
            return True









with open("property_information.json") as f:
    file = json.load(f)
    f.close()




