import random
import json
from constants import *
from board import Board
from player import Player


def dice_roll():
    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    n = True if dice1 == dice2 else False
    return dice1+dice2, n

def import_instructions():
    with open("instructions_writing.json") as f:
        file = json.load(f)
        f.close()
    return file


def write_instructions(
        win):  # calculates how many characters can go on each line, where they are drawn to and then draws the text to the screen
    instructions = import_instructions()  # gets the text from a JSON file
    letter_height = (INSTRUCTION_FONT.render("H", False, (
    0, 0, 0))).get_height()  # calculates the height a letter will be using the font size selected
    start_pos = WINDOW_WIDTH * 13 / 320
    for instruction in instructions:  # going through each instruction in the 11 instructions written for each screenshot
        instruction_list = render_instruction_text(font, instructions[instruction], COLOURS["BLACK"], WINDOW_WIDTH - (
                2 * WINDOW_WIDTH * 3 / 20))  # seperates the instruction into a list each element contains the maximum amount of characters that can fit in the space given
        new_line = start_pos  # gets the starting position for the instruction
        for line in instruction_list:  # goes through the text elements in the instruction list and draws them to the screen
            render_text(win, INSTRUCTION_FONT, line, COLOURS["BLACK"], (WINDOW_WIDTH / 2, new_line))
            new_line += letter_height  # before it draws the next series of text from the same instruction it adds the letter height so the next bit of text is just underneath
        start_pos += int(
            SQUARE_MEASUREMENTS / 12)  # adds 1/12 of the height as the 11 images are evenly spread going down the window


def calculate_picture_size(
        picture):  # calculates the correct re-size of the image depending on it's actual height and width
    width = picture.get_width()
    height = picture.get_height()
    if -5 < width - height < 5:  # if the width and height are similar then the image will be drawn square
        width = WINDOW_WIDTH * 21 / 256
    elif width > height:
        width = WINDOW_WIDTH * 3 / 20
    else:
        width = WINDOW_WIDTH * 7 / 128
    height = WINDOW_WIDTH * 21 / 256
    return int(width), int(height)
