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
SQUARE_MEASUREMENTS = int(WINDOW_WIDTH * 35 / 64)#700
PROPERTY_WIDTH = WINDOW_WIDTH * 3 / 64#60
PROPERTY_HEIGHT = WINDOW_WIDTH * 1 / 16#80
PROPERTY_ENLARGE_WIDTH = WINDOW_WIDTH*5/16#
PROPERTY_ENLARGE_HEIGHT = WINDOW_WIDTH*13/32

BUTTON_WIDTH = WINDOW_WIDTH*15/128
BUTTON_HEIGHT = WINDOW_WIDTH*5/64


game_finished = False


#property figures
number_of_properties = 40



#player figures
starting_money = 1500
free_parking_cash = 0


#functions used by most files

pygame.font.init()
font = pygame.font.SysFont('arial', int(WINDOW_WIDTH*13/640))
title_font = pygame.font.SysFont('arial', 300)
winner_font = pygame.font.SysFont('arial', 200)
INSTRUCTION_FONT = pygame.font.SysFont('arial', 16)

def get_centre(font, message,colour):
    text_surface = font.render(message, False, colour)
    return text_surface, text_surface.get_rect()

def render_text(win, font, message, colour, co_ords):
    text_surf, text_rect = get_centre(font, message, colour)
    text_rect.center = co_ords
    win.blit(text_surf,text_rect)

def render_instruction_text(font, message, colour, max_length):
    text_width = (font.render(message, False, colour)).get_width()
    if text_width > max_length:
        max_character = calculate_text_length(message, max_length, 0, len(message))
    else:
        max_character = len(message)-1
    return calculate_text_for_display(max_character,message)


def calculate_text_length(message, max_length, start, end):
    middle = ((start+end)//2)
    half_message_width = INSTRUCTION_FONT.render((message[:middle]), False, (0,0,0)).get_width()
    next_character_width = INSTRUCTION_FONT.render((message[:middle+1]), False, (0,0,0)).get_width()#TODO change font to INSTRUCTION_FONT
    if half_message_width<= max_length <= next_character_width or INSTRUCTION_FONT.render(message, False, (0,0,0)).get_width() < max_length:
        return middle
    elif half_message_width > max_length:
        return calculate_text_length(message, max_length, start, middle)
    else:
        return calculate_text_length(message, max_length, middle, end)


def calculate_text_for_display(max_characters, message):
    message_list = []
    start_character = 0
    end_character = max_characters
    for i in range((len(message) // max_characters) + (len(message) % max_characters > 0)+1):
        if start_character + max_characters >= len(message)-1:
            message_list.append(message[start_character:(len(message)+1)])
            break
        else:
            end_character = find_space(message[start_character:], end_character)
            message_list.append(message[start_character:start_character+end_character])
            start_character+=end_character+1
    return message_list

def find_space(message, end_character):
    if message[end_character] == " ":
        return end_character
    else:
        return find_space(message, end_character-1)