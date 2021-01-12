import json
from constants import *
pygame.init()


"""the board document will primarily deal with the graphics side of the gamne, drawing the board and items when a command is executed"""


class Board(pygame.Surface):   #this inherits from the pygame.surface class
    def __init__(self, width, height):
        super().__init__((width, height)) #this allows me to use the methods and attributes of the pygame.surface class
        #self.cards = []
        self.properties = [] #this will be filled with instances of the property class
        self.SORTED_SETS = {
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
        }#this will contain the instances of the property class but sorted into their coloured sets
        """this could probably be shortened somehow"""
        starting_value = SQUARE_MEASUREMENTS - PROPERTY_HEIGHT
        self.properties.append(Property("corner", starting_value, starting_value, *file[str(len(self.properties))].values()))
        for i in range(9):
            self.properties.append(Property( "vert", (starting_value - PROPERTY_WIDTH) - (i * PROPERTY_WIDTH), starting_value, *file[str(len(self.properties))].values()))
        self.properties.append(Property("corner", 0, starting_value, *file[str(len(self.properties))].values()))
        for i in range(9):
            self.properties.append(Property("hori", 0, (starting_value - PROPERTY_WIDTH) - (i * PROPERTY_WIDTH), *file[str(len(self.properties))].values()))

        self.properties.append(Property("corner", 0,0, *file[str(len(self.properties))].values()))
        for i in range(9):
            self.properties.append(Property("vert", PROPERTY_HEIGHT + (i * PROPERTY_WIDTH), 0, *file[str(len(self.properties))].values()))

        self.properties.append(Property("corner", SQUARE_MEASUREMENTS - PROPERTY_HEIGHT, 0, *file[str(len(self.properties))].values()))
        for i in range(9):
            self.properties.append(Property("hori", SQUARE_MEASUREMENTS - PROPERTY_HEIGHT, PROPERTY_HEIGHT + (i * PROPERTY_WIDTH), *file[str(len(self.properties))].values()))



        self.buttons = [[Button("ROLL DICE", SQUARE_MEASUREMENTS / 2, SQUARE_MEASUREMENTS / 2, COLOURS["GREEN"], True)],

                        [
                        Button("LOOK AT PROPERTIES", SQUARE_MEASUREMENTS / 2, SQUARE_MEASUREMENTS * 2 / 7, COLOURS["YELLOW"], True),
                        Button("END TURN", SQUARE_MEASUREMENTS / 2, SQUARE_MEASUREMENTS / 2, COLOURS["RED"], True),
                        Button("MAKE DEAL", SQUARE_MEASUREMENTS / 2, 150 + SQUARE_MEASUREMENTS / 2, COLOURS["PINK"], True)
                        ],

                        [Button("PURCHASE", WINDOW_WIDTH * 13 / 64, WINDOW_WIDTH*55/128, COLOURS["GREEN"], True),
                         Button("AUCTION", WINDOW_WIDTH*41/128, 9 * PROPERTY_WIDTH + 10, COLOURS["DARK BLUE"], True)],


                        [Button("FINISHED", WINDOW_WIDTH*35/128, WINDOW_WIDTH*109/256, COLOURS["GREEN"], True),
                         Button("+1", WINDOW_WIDTH*17/256, WINDOW_WIDTH*13/32, COLOURS["GREEN"], False, WINDOW_WIDTH*3/64, WINDOW_WIDTH*3/128),
                         Button("+10", WINDOW_WIDTH*29/256, WINDOW_WIDTH*13/32, COLOURS["GREEN"], False, WINDOW_WIDTH*3/64, WINDOW_WIDTH*3/128),
                         Button("+100", WINDOW_WIDTH*41/256, WINDOW_WIDTH*13/32, COLOURS["GREEN"], False, WINDOW_WIDTH*3/64, WINDOW_WIDTH*3/128),
                         Button("-1", WINDOW_WIDTH*17/256, WINDOW_WIDTH*59/128, COLOURS["RED"], False, WINDOW_WIDTH*3/64, WINDOW_WIDTH*3/128),
                         Button("-10", WINDOW_WIDTH*29/256, WINDOW_WIDTH*59/128, COLOURS["RED"], False, WINDOW_WIDTH*3/64, WINDOW_WIDTH*3/128),
                         Button("-100", WINDOW_WIDTH*41/256, WINDOW_WIDTH*59/128, COLOURS["RED"], False, WINDOW_WIDTH*3/64, WINDOW_WIDTH*3/128),
                         Button("+1 ", WINDOW_WIDTH*87/256, WINDOW_WIDTH*13/32, COLOURS["GREEN"], False, WINDOW_WIDTH*3/64, WINDOW_WIDTH*3/128),
                         Button("+10 ", WINDOW_WIDTH*99/256, WINDOW_WIDTH*13/32, COLOURS["GREEN"], False, WINDOW_WIDTH*3/64, WINDOW_WIDTH*3/128),
                         Button("+100 ", WINDOW_WIDTH*111/256, WINDOW_WIDTH*13/32, COLOURS["GREEN"], False, WINDOW_WIDTH*3/64, WINDOW_WIDTH*3/128),
                         Button("-1 ", WINDOW_WIDTH*87/256, WINDOW_WIDTH*59/128, COLOURS["RED"], False, WINDOW_WIDTH*3/64, WINDOW_WIDTH*3/128),
                         Button("-10 ", WINDOW_WIDTH*99/256, WINDOW_WIDTH*59/128, COLOURS["RED"], False, WINDOW_WIDTH*3/64, WINDOW_WIDTH*3/128),
                         Button("-100 ", WINDOW_WIDTH*111/256, WINDOW_WIDTH*59/128, COLOURS["RED"], False, WINDOW_WIDTH*3/64, WINDOW_WIDTH*3/128)
                         ],

                        [Button("ACCEPT", PROPERTY_HEIGHT, WINDOW_WIDTH*13/32, COLOURS["GREEN"], False, WINDOW_WIDTH*9/64, WINDOW_WIDTH*3/128),
                         #Button("COUNTER", PROPERTY_HEIGHT + (SQUARE_MEASUREMENTS - 2*PROPERTY_HEIGHT)/3, PROPERTY_HEIGHT+ 9*PROPERTY_WIDTH - BUTTON_HEIGHT, COLOURS["ORANGE"], False, (SQUARE_MEASUREMENTS - 2*PROPERTY_HEIGHT)/3),
                         Button("REJECT", WINDOW_WIDTH*11/32, WINDOW_WIDTH*13/32, COLOURS["RED"], False, (SQUARE_MEASUREMENTS - 2 * PROPERTY_HEIGHT) / 3, WINDOW_WIDTH*3/128)
                        ],

                        [Button("+ HOUSE", WINDOW_WIDTH*15/128, WINDOW_WIDTH*25/64, COLOURS["GREEN"], False, WINDOW_WIDTH*5/32, WINDOW_WIDTH*5/128),
                         Button("- HOUSE", WINDOW_WIDTH*15/128, WINDOW_WIDTH*55/128, COLOURS["RED"], False, WINDOW_WIDTH*5/32, WINDOW_WIDTH*5/128),
                         Button("MORTGAGE", WINDOW_WIDTH*35/128, WINDOW_WIDTH*25/64, COLOURS["GREEN"], False, WINDOW_WIDTH*5/32, WINDOW_WIDTH*5/128),
                         Button("UNMORTGAGE", WINDOW_WIDTH*35/128, WINDOW_WIDTH*55/128, COLOURS["RED"], False, WINDOW_WIDTH*5/32, WINDOW_WIDTH*5/128),
                         ],#player property actions - mortgage, buy houses etc.

                        [Button("BID 100", WINDOW_WIDTH*9/128, WINDOW_WIDTH*25/64, COLOURS["RED"], False, PROPERTY_ENLARGE_WIDTH / 3),
                         Button("BID 10", WINDOW_WIDTH*67/384, WINDOW_WIDTH*25/64, COLOURS["ORANGE"], False, PROPERTY_ENLARGE_WIDTH / 3),
                         Button("BID 1", WINDOW_WIDTH*107/384, WINDOW_WIDTH*25/64, COLOURS["PINK"], False, PROPERTY_ENLARGE_WIDTH / 3),
                         Button("LEAVE", WINDOW_WIDTH*15/128, PROPERTY_HEIGHT, COLOURS["RED"], False, 2 * PROPERTY_HEIGHT, PROPERTY_WIDTH / 2)],

                        ]

        self.occuring_button = Button("BANK", WINDOW_WIDTH*113/128, 0, COLOURS["RED"], False), Button("BACK", WINDOW_WIDTH*35/128, WINDOW_WIDTH*19/256, COLOURS["RED"], True, PROPERTY_HEIGHT, PROPERTY_WIDTH / 2)







    def sort_sets(self):
        for property in self.properties:
            if property.purchase != None:#if the property has a purchase value that it is one that can be obtained by the player and thus has a set
                self.SORTED_SETS[list(COLOURS.keys())[list(COLOURS.values()).index(property.colour)]].append(property)
                # the line above finds the correct colour set for each property it does it by finding the index value
                # of the property colour in the values of the COLOURS dictionary. That number corresponds to the
                # value and key in the dictionary, so the COLOURS keys become a list and the value obtained is the
                # index to find the correct colour and the property is then appended into that colour




    def draw_background(self, list_of_players, turn):
        self.fill((200, 200, 255))#fills the background a light blue colour
        for p in self.properties: #this goes through all the properties and draws them to the board
            p.draw_propertys(self)
        for player_index in range(len(list_of_players)):#goes through the players and draws their player squares on the board
            list_of_players[player_index]. draw_player_square(self, player_index, SQUARE_MEASUREMENTS/len(list_of_players),turn)

    def draw_onto_board(self,player_pos, action_taken, other_card):
        self.draw_action(action_taken, player_pos, other_card) #this will draw graphics on the screen depending on what happens
        self.draw_buttons(action_taken)

    def draw_buttons(self, action_taken):
        self.occuring_button[0].draw(self)  # the bankrupt button will always be drawn
        if action_taken == 3 or action_taken == 5 or action_taken == 11:  # draws the back button if make deal, look at propertys or property is clicked on
            self.occuring_button[1].draw(self)
        if action_taken < 7:  # the buttons_list can only have 7 maximum as it's index and thus needs this to prevent errors happening
            for b in self.buttons[action_taken]:  # goes through the buttons drawing them to the screen
                b.draw(self)




    def draw_action(self, action_taken, player_pos, other_card):
        pos = player_pos if other_card == None else other_card#if other_card = None then the player is dealing with the property their on if it doesn't then they're dealing with a property they're not on
        current_property = self.properties[pos]#finds the property the game is focusing on
        if action_taken == 2 or action_taken == 5 or action_taken == 7:#these are when a purchase, a player looking at their propertys or paying rent happens
            current_property.enlarge_property(self,1) #this draws the enlarged property card to the screen

            if action_taken == 7:#when paying rent occurs
                n = 2 if current_property.full_set == True and current_property.amount_houses == 0 else 1 #if the player had a full set then the rent just for the card is doubled this will display the amount the rent will be
                render_text(self, font,f'{current_property.owned.username} owns this property you paid {n*current_property.rent[str(current_property.amount_houses)]}'
                            , COLOURS["BLACK"], (WINDOW_WIDTH*13/64, WINDOW_WIDTH*55/128))

        elif action_taken == 8 or action_taken == 9:#when a player lands on community chest, tax or chance property
            current_property.enlarge_card(self)#draws a card to the board with the information about where they landed
            """if action_taken == 9:
                x = random.randint(0,len(self.cards)-1)
                render_text(self, font, f'{self.cards[x].text}', COLOURS["BLACK"],(300,300))"""


            """

    def enlarge_property(self):
        print("Get the fock out of town")
        for property in self.properties:
            if property.check_for_click_prop(): #checks if players cursor is on a property, returns True if it is.
                if property.purchase != None:#if it has a purchase value then the player can obtain and interact with it
                    property.enlarge_property(self,1)
                    return self.properties.index(property)
                elif property.height != property.width :
                    property.enlarge_card(self)
                    
                    """
    def check_for_button_click(self, action_taken):
        if action_taken < 7:#the buttons list maximum index is 7 so action_taken has to be lower
            for button in self.buttons[action_taken]:
                if button.check_for_press():#checks if player's co_ords are on button, returns True if it is
                    return button.text #returns what is written on the button
        if action_taken == 3 or action_taken == 5 or action_taken == 11:#this is when the back button will be drawn
            if self.occuring_button[1].check_for_press():#checks if the players co_ords are on the back button, returns True if they are
                return self.occuring_button[1].text #returns "BACK", what is written on the button
        if self.occuring_button[0].check_for_press():#checks if player co_ords are on the BANKRUPT button
            return self.occuring_button[0].text#returns "BANKRUPT"



    def utility_station_rent(self, colour):
        # this is used for the station and utility propertys as the rent works differently to the other propertys.
        # The function finds out who owns the propertys and how many they own and then changes the houses value to
        # fit with how many each player has
        owned_players = [] #list where the players who own the property will be appended to
        for p in self.SORTED_SETS[colour]:#uses the colour as a key to SORTED_SETS dictionary to find the propertys that have that colour
            owned_players.append(p.owned)#appends the player who owns the property
        counts = [[username, owned_players.count(username)] for username in set(owned_players)]#the set removes any repeats so if the player owns 2 they'll only be in the set once.
        for i in range(len(counts)): #It then goes through the players in the set and counts how many times they appear in the owned_propertys
            if counts[i][0] != None:#If the username is None it means nobody owns the property
                for p in self.SORTED_SETS[colour]:
                    if p.owned == counts[i][0]:
                        p.amount_houses = counts[i][1] -1

    def no_deal_player(self):
        pygame.draw.rect(self, COLOURS["BLACK"], (PROPERTY_HEIGHT, 150 + SQUARE_MEASUREMENTS / 2, SQUARE_MEASUREMENTS, PROPERTY_WIDTH))



    def convert_for_send(self, pl_list): #This goes through the propertys in the game and returns a list with all the property information that could change over the course of a game.
        prop_list = []                   #It goes through which player owns the property and returns their index in the pl-list to be sent over this is so an integer is being sent instead of the player instance.
        for prop in self.properties:
            prop_index = prop.owned
            if prop.owned is not None:#This means the property is owned by a player.
                prop_index = pl_list.index(prop.owned)
            prop_list.append([prop.mortgage, prop_index, prop.amount_houses, prop.full_set])#these variables can change over a game they are integers and TRUE/FALSE.
        return prop_list #returns the variables that change for each property in the same order that they go around the board in.

    def convert_for_use(self, send_board, pl_list): #this is used in the client to update their instance of the board class
        for prop_num in range(len(send_board)):#this will go through all the property information that could've changed. The send-board info will be in the same order as the self.properties list
            self.properties[prop_num].mortgage = send_board[prop_num][0]  #changing the mortgage value to the one sent over
            try:#TODO remove try and except clauses
                self.properties[prop_num].owned = pl_list[send_board[prop_num][1]] if send_board[prop_num][1] is not None else None #if it does not equal None then it is a player_index and thus the property.owned will return back to the player instance who owns it
            except:
                print(send_board[prop_num][1])
            self.properties[prop_num].amount_houses = send_board[prop_num][2]
            self.properties[prop_num].full_set = send_board[prop_num][3]










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
        pygame.draw.rect(win, self.colour, self.find_colour_box_pos())
        if self.owned is not None:
            pygame.draw.rect(win,self.owned.colour,(self.x, self.y, self.width, self.height),5) #this will draw the players icon on the property to show who owns it
        if self.houses_price is not None:
            self.draw_houses(win)
        if self.mortgage:
            pygame.draw.line(win, COLOURS["RED"], (self.x, self.y), (self.x + self.width, self.y + self.height))
        pygame.draw.rect(win, COLOURS["BLACK"], (self.x, self.y, self.width, self.height), 1)
    """create a function which manages the text so it fits within the property space"""

    def find_row(self):
        if self.width > self.height:
            if self.x < SQUARE_MEASUREMENTS/2:
                return "LEFT"
            else:
                return "RIGHT"
        else:
            if self.y > SQUARE_MEASUREMENTS/2:
                return "BOTTOM"
            else:
                return "TOP"

    def find_colour_box_pos(self):
        row = self.find_row()
        if row == "LEFT":
            colour_box = (self.x + PROPERTY_HEIGHT*3/4, self.y, self.width / 4, self.height)
        elif row == "RIGHT":
            colour_box = (self.x, self.y, self.width/4, self.height)
        elif row == "BOTTOM":
            colour_box = (self.x, self.y, self.width, self.height / 4)
        else:
            colour_box = (self.x, self.y + 3/4*PROPERTY_HEIGHT, self.width, self.height / 4)
        return colour_box

    def draw_houses(self, win):
        if self.amount_houses == 5:
            pygame.draw.rect(win, COLOURS["RED"], self.draw_hotel())
        else:
            render_text(win, font, str(self.amount_houses), COLOURS["GREEN"], (40 + self.x, self.y + 40))

    def draw_hotel(self):
        row = self.find_row()
        if row == "LEFT":
            return (self.x + self.height/4, self.y + PROPERTY_WIDTH/2, 20, 20)
        elif row == "RIGHT":
            return (self.x + (PROPERTY_HEIGHT/4)*3, self.y + PROPERTY_WIDTH / 2, 20, 20)
        elif row == "BOTTOM":
            return (self.x + PROPERTY_WIDTH/2, self.y + (PROPERTY_HEIGHT/4)*3, 20, 20)
        else:
            return (self.x + PROPERTY_WIDTH/2, self.y + PROPERTY_HEIGHT/4, 20, 20)


    def property_actions(self, player):
        if self.purchase != None and self.owned == None: #this means it's an unowned property card
            return 2
        elif self.purchase != None and self.owned != None and self.owned != player and self.mortgage == False:#this means it's an owned property
            return 7
        elif self.purchase == None and self.rent != None:#this means it is a tax card
            return 8
        elif self.name == "COMMUNITY CHEST":
            return 9
        elif self.name == "CHANCE":
            return 1
        else:
            return 1







    def check_for_click_prop(self):
        x, y = pygame.mouse.get_pos()
        if pygame.Rect(self.x,self.y,self.width,self.height).collidepoint(x,y):
            return True

    def enlarge_property(self, win, pos):#this is graphically used to show a card which can be purchased onto the board
        starting_x = PROPERTY_HEIGHT + (PROPERTY_WIDTH * pos)  # if pos = 0 the property is on the left, 1 makes the property in the middle and 2 will put it on the right
        pygame.draw.rect(win, COLOURS["WHITE"], (starting_x, PROPERTY_HEIGHT, 7 * PROPERTY_WIDTH, 9 * PROPERTY_WIDTH))
        pygame.draw.rect(win, COLOURS["BLACK"], (starting_x + WINDOW_WIDTH*1/128, WINDOW_WIDTH*9/128, WINDOW_WIDTH*5/16, WINDOW_WIDTH*13/32), 1)
        colour_box = (starting_x + WINDOW_WIDTH*1/64,WINDOW_WIDTH*5/64, WINDOW_WIDTH*19/64, WINDOW_WIDTH*1/16)
        x, y = pygame.Rect(colour_box).center
        if self.houses_price is not None:
            self.draw_house_information(win, colour_box, x ,y)
        else:
            if len(self.rent) > 2:
                self.draw_station_information(win, x, y)
            else:
                self.draw_utility_information(win, x, y)
        render_text(win, font, self.name, COLOURS["BLACK"], (x, y))


    def draw_house_information(self, win, colour_box, x ,y):
        pygame.draw.rect(win, self.colour, colour_box)
        render_text(win, font, self.name, COLOURS["BLACK"], (x, y))
        for i in range(len(self.rent)):
            render_text(win, font, f'Rent with {str(i)} house {self.rent[str(i)]}', COLOURS["BLACK"],
                        (x, y + PROPERTY_WIDTH + i * PROPERTY_WIDTH / 2))
        render_text(win, font, f'Mortgage value {int(self.purchase / 2)}', COLOURS["BLACK"],
                    (x, y + 9 * PROPERTY_WIDTH / 2))
        render_text(win, font, f'Houses cost {self.houses_price} each', COLOURS["BLACK"],
                    (x, y + 5 * PROPERTY_WIDTH))
        render_text(win, font, f'Hotels, {self.houses_price} each plus 4 houses', COLOURS["BLACK"],
                    (x, y + 11 * PROPERTY_WIDTH / 2))

    def draw_station_information(self, win,x,y):
        for i in range(len(self.rent)):
            render_text(win, font, f'Rent with {str(i + 1)} stations {self.rent[str(i)]}', COLOURS["BLACK"],
                        (x, y + 2 * PROPERTY_WIDTH + i * PROPERTY_WIDTH / 2))
        render_text(win, font, f'MORTGAGE VALUE - {int(self.purchase / 2)}', COLOURS["BLACK"],
                    (x, y + 5 * PROPERTY_WIDTH))

    def draw_utility_information(self, win, x, y):
        for i in range(len(self.rent)):
            render_text(win, font,
                        f'If {str(i + 1)} "utility" is owned rent is {self.rent[str(i)]} times amount shown on dice',
                        COLOURS["BLACK"], (x, y + 4 * PROPERTY_WIDTH + i * PROPERTY_WIDTH / 2))


    def enlarge_card(self, win):
        pygame.draw.rect(win, COLOURS["WHITE"], (PROPERTY_HEIGHT, WINDOW_WIDTH*7/64, WINDOW_WIDTH*27/64, WINDOW_WIDTH*21/64))
        line = (PROPERTY_HEIGHT, WINDOW_WIDTH*7/64, WINDOW_WIDTH*27/64, WINDOW_WIDTH*21/64)
        pygame.draw.rect(win, COLOURS["BLACK"], line,1)
        x,y = pygame.Rect(line).center
        render_text(win,font, f'{self.name}', COLOURS["ORANGE"], (x,y))
        if self.rent is not None: #this means they have landed on a tax card and I can use the center co-ordinates instead of re-doing them in the draw_action function
            render_text(win, font, f'You owe {self.rent}', COLOURS["RED"], (x, y + PROPERTY_WIDTH))

class Button:
    def __init__(self, text, x, y, color, centre, width = BUTTON_WIDTH, height = BUTTON_HEIGHT):
        self.text = text
        self.color = color
        self.width = width
        self.height = height
        self.x = x - self.width / 2 if centre is True else x
        self.y = y - self.height / 2 if centre is True else y

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