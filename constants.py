import pygame
import textwrap
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
have_enough_money = True


#property figures
number_of_properties = 40



#player figures
starting_money = 300
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


