import pygame
# Colours
BROWN = (179,116,6)
LIGHT_BLUE = (137,224,255)
PINK = (255,0,137)
ORANGE = (255,145,0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255,239,0)
GREEN = (0, 255, 0)
DARK_BLUE = (0, 0, 255)
WHITE = (255,255,255)

# Dimensions
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = int(WINDOW_WIDTH*35/64)#700
PROPERTY_WIDTH = WINDOW_WIDTH * 3/64#80
PROPERTY_HEIGHT = WINDOW_WIDTH* 1/16#60
BOARD_WIDTH = WINDOW_WIDTH * 35/64#700

#property figures
number_of_properties = 40



#player figures
starting_money = 1500



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
