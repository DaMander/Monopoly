import pygame
import json
from constants import *
from player import Player
pygame.init()


"""the board document will primarily deal with the graphics side of the gamne, drawing the board and items when a command is executed"""


class Board(pygame.Surface):   #this class creates the 40 instances of the location class needed fot the 40 propertys in monopoly
    def __init__(self, width, height):
        super().__init__((width, height))
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


        self.buttons = [[Button("ROLL DICE", BOARD_WIDTH/2, WINDOW_HEIGHT/2, COLOURS["GREEN"], True)],
                        [Button("END TURN", BOARD_WIDTH/2, WINDOW_HEIGHT/2, COLOURS["RED"], True), Button("MAKE DEAL", BOARD_WIDTH/2, 150 + WINDOW_HEIGHT/2, COLOURS["PINK"], True), Button("LOOK AT PROPERTYS", BOARD_WIDTH/2,  WINDOW_HEIGHT/2 -150, COLOURS["YELLOW"], True)],
                        [Button("PURCHASE", PROPERTY_HEIGHT + PROPERTY_WIDTH + 120, 9 * PROPERTY_WIDTH +10, COLOURS["GREEN"], True), Button("AUCTION", PROPERTY_HEIGHT + PROPERTY_WIDTH + 270, 9 * PROPERTY_WIDTH +10, COLOURS["DARK BLUE"], True)],
                        [],
                        [],
                        [Button("DONE", BOARD_WIDTH/2, WINDOW_HEIGHT/2, COLOURS["BLACK"], True)]
                        ]

        self.always_button = Button("BANK", WINDOW_WIDTH-150,0,COLOURS["RED"], False) #this button will be used for the player to delcare bankruptcy

    def sort_sets(self):
        for p in self.properties:
            if p.purchase != None:
                self.sorted_sets[list(COLOURS.keys())[list(COLOURS.values()).index(p.colour)]].append(p)





    def draw(self, list_of_players, player_pos, action_taken):

        self.fill((200, 200, 255))
        for p in self.properties:
            p.draw_propertys(self)
        for i in range(len(list_of_players)):
            list_of_players[i].draw_player_square(self, BOARD_WIDTH, i, WINDOW_WIDTH-BOARD_WIDTH, WINDOW_HEIGHT/len(list_of_players))
        self.draw_action(action_taken, player_pos) #this will draw graphics on the screen depending on what happens
        self.always_button.draw(self) #this will draw buttons that are always on the screen
        if action_taken <4:
            for b in self.buttons[action_taken]:
                b.draw(self)

            #this will draw all the propertys onto the board using the draw function in the Property class



    def draw_action(self, action_taken, player_pos):
        current_property = self.properties[player_pos]
        if action_taken == 2 or action_taken == 6:
            current_property.enlarge_property(self)
            if action_taken == 6:
                render_text(self, font,f'{current_property.owned.username} owns this property you paid {current_property.rent[str(current_property.amount_houses)]}'
                            , COLOURS["BLACK"], (PROPERTY_HEIGHT + PROPERTY_WIDTH + 120, 9 * PROPERTY_WIDTH +10))



    def enlarge_property(self):
        for p in self.properties:
            if p.check_for_click_prop() and p.houses_price != None:
                p.enlarge_property(self)

    def check_for_button_click(self, which_buttons):
        if which_buttons < 5:
            for b in self.buttons[which_buttons]:
                return b.check_for_press()








class Property(pygame.Surface): #this class is used when drawing the squares to the board, used in the Board class to allow all the instances of location to be added to a list
    def __init__(self, orientation, x, y, name, purchase = None, rent = None, mortgage = None, houses_price = None, colour = "BOARD COLOUR"):
        super().__init__((PROPERTY_WIDTH, PROPERTY_HEIGHT))
        self.width = PROPERTY_WIDTH if orientation == "vert" else PROPERTY_HEIGHT
        self.height = PROPERTY_WIDTH if orientation == "hori" else PROPERTY_HEIGHT
        self.x = x
        self.y = y
        self.name = name
        self.purchase = purchase
        self.rent = rent
        self.mortgage = mortgage
        self.houses_price = houses_price
        self.colour = COLOURS[colour]
        self.owned = None
        self.amount_houses = 0
        #COLOUR

    def draw_propertys(self, win):
        self.fill((200, 200, 255))

        n = (self.x, self.y, self.width / 4, self.height) if self.width > self.height else (self.x, self.y, self.width, self.height / 4)
        pygame.draw.rect(win, self.colour, (n))
        #if self.owned != None:
         #   pygame.draw.circle(win, self.owned.colour, (100,100),30) this will draw the players icon on the property to show who owns it
        pygame.draw.rect(win, COLOURS["BLACK"], (self.x, self.y, self.width, self.height), 1)
    """create a function which manages the text so it fits within the property space"""

    def property_actions(self):
        if self.purchase != None and self.owned == None: #this means it's an unowned property card
            return 2
        elif self.purchase != None and self.owned != None:#this means it's an owned property
            return 6
        elif self.purchase == None and self.rent != None:#this means it is a tax card
            return 7
        elif self.name == "COMMUNITY CHEST":
            return 1
        elif self.name == "CHANCE":
            return 1
        else:
            return 1






    def check_for_click_prop(self):
        x, y = pygame.mouse.get_pos()
        if pygame.Rect(self.x,self.y,self.width,self.height).collidepoint(x,y):
            return True

    def enlarge_property(self,win):
        pygame.draw.rect(win, COLOURS["WHITE"], (PROPERTY_HEIGHT+PROPERTY_WIDTH, PROPERTY_HEIGHT, 7*PROPERTY_WIDTH, 9*PROPERTY_WIDTH))
        pygame.draw.rect(win, COLOURS["BLACK"], (PROPERTY_HEIGHT + PROPERTY_WIDTH + 10, PROPERTY_HEIGHT + 10, 7 * PROPERTY_WIDTH -20,9 * PROPERTY_WIDTH -20),1)
        colour_box = (PROPERTY_HEIGHT + PROPERTY_WIDTH + 20, PROPERTY_HEIGHT + 20, 7 * PROPERTY_WIDTH -40,2 * PROPERTY_WIDTH -40)
        x,y = pygame.Rect(colour_box).center
        pygame.draw.rect(win, self.colour, colour_box)
        render_text(win, font, self.name, COLOURS["BLACK"], (x,y))
        for i in range(len(self.rent)):
            render_text(win, font, f'Rent with {str(i)} house {self.rent[str(i)]}', COLOURS["BLACK"], (x, y + 60 + i*30 ))
        render_text(win, font, f'Mortgage value {self.mortgage}', COLOURS["BLACK"], (x, y +260))
        render_text(win, font, f'Houses cost {self.houses_price} each', COLOURS["BLACK"], (x,y +300))
        render_text(win, font, f'Hotels, {self.houses_price} each plus 4 houses', COLOURS["BLACK"], (x,y+340))


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
        font = pygame.font.SysFont("comicsans", int(WINDOW_WIDTH*1/32))
        text = font.render(self.text, 1, (255,255,255))
        win.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2)))

    def check_for_press(self):
        x,y = pygame.mouse.get_pos()
        if pygame.Rect(self.x,self.y, self.width, self.height).collidepoint(x,y):
            return self.text









with open("property_information.json") as f:
    file = json.load(f)




