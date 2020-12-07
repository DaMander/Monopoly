import pygame
# Colours
COLOURS = {
    "BROWN" : (179,116,6),
    "LIGHT BLUE" : (137,224,255),
    "PINK" : (255,0,137),
    "ORANGE" : (255,145,0),
    "BLACK" : (0, 0, 0),
    "RED" : (255, 0, 0),
    "YELLOW" : (255,239,0),
    "GREEN" : (0, 255, 0),
    "DARK BLUE" : (0, 0, 255),
    "WHITE" : (255,255,255),
    "BOARD COLOUR": (200, 200, 255)
}


# Dimensions
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = int(WINDOW_WIDTH*35/64)#700
PROPERTY_WIDTH = WINDOW_WIDTH * 3/64#80
PROPERTY_HEIGHT = WINDOW_WIDTH* 1/16#60
BOARD_WIDTH = WINDOW_WIDTH * 35/64#700
PROPERTY_ENLARGE_WIDTH = 7 * PROPERTY_WIDTH - (2 * 1/6*PROPERTY_WIDTH)
PROPERTY_ENLARGE_HEIGHT = 9 * PROPERTY_WIDTH - (2 * 1/6*PROPERTY_WIDTH)

BUTTON_WIDTH = WINDOW_WIDTH*15/128
BUTTON_HEIGHT = WINDOW_WIDTH*5/64

#fixed variables, stay the same each start of game
auction = None
deal = None
have_enough_money = True
deal_player = None
amount_required = 0
turn = 0
#turn is used to go through each player to let them have there turn
triple_checker = 0
#this variable checks whether a player has rolled three doubles in a row
action_taken = 0
#this number will change depending on where the player lands it'll decide which buttons are drawn and what actions the player can take
double = False
#when a player rolls a double they can still purchase or pay rent to property so when it's complete this will validate whether there at the end of their turn
action_time = 0
#this will be used for timers or delays
other_card = None
#used when dealing with a property that the player is not on
jail_list = []

#property figures
number_of_properties = 40



#player figures
starting_money = 1500
free_parking_cash = 0


#functions used by most files

pygame.font.init()
font = pygame.font.SysFont('arial', int(WINDOW_WIDTH*13/640))

def get_centre(font, message,colour):
    text_surface = font.render(message, False, colour)
    return text_surface, text_surface.get_rect()

def render_text(win, font, message, colour, co_ords):
    text_surf, text_rect = get_centre(font, message, colour)
    text_rect.center = co_ords
    win.blit(text_surf,text_rect)