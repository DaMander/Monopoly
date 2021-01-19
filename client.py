import json
import traceback

from player import *
from constants import *
from game_rules import *
from network import Network
from board import Button
import sys

start_screen_buttons = [
    Button("START GAME", WINDOW_WIDTH / 4, 3 * SQUARE_MEASUREMENTS / 4, COLOURS["GREEN"], True, int(WINDOW_WIDTH / 5)),
    Button("INSTRUCTIONS", WINDOW_WIDTH/2, 3*SQUARE_MEASUREMENTS/4, COLOURS["BROWN"], True, int(WINDOW_WIDTH/5)),
    Button("BACK", WINDOW_WIDTH//2,WINDOW_WIDTH*1/64, COLOURS["RED"], True, BUTTON_WIDTH, WINDOW_WIDTH*1/32)]#as the board class is not initialised yet these buttons are only used to start the game

wait_for_players_buttons= [Button("START", SQUARE_MEASUREMENTS / 2, 3 * SQUARE_MEASUREMENTS / 4, COLOURS["GREEN"], True, int(WINDOW_WIDTH / 3))]


def draw_start_screen():#draws the first screen you see when you start the client
    win.fill((200, 255, 200))
    render_text(win, title_font, "Monopoly", (255, 0, 0), (WINDOW_WIDTH / 2, SQUARE_MEASUREMENTS / 4))
    start_screen_buttons[0].draw(win)
    start_screen_buttons[1].draw(win)


def show_instructions():#when player clicks instructions button this will draw the graphics to the screen
    pygame.draw.rect(win, (200, 255, 200), (0, 0, WINDOW_WIDTH, SQUARE_MEASUREMENTS))
    start_screen_buttons[2].draw(win)#draws BACK button
    draw_screenshots()
    write_instructions()


def draw_screenshots():#draws screenshots of the game to explain the instructions
    for image_no in range(1, 12):#I called the images 1,2,3,4, etc. so I could use a for loop to acess them easier
        screenshot = pygame.image.load(f"Game_screenshots/{str(image_no)}.png")
        width, height = calculate_picture_size(screenshot)#calculates the picture size depending on how big the window width is
        screenshot = pygame.transform.scale(screenshot,(width,height))#the image is re-sized to what will fit on the screen
        win.blit(screenshot, (((image_no-1)%2)*(WINDOW_WIDTH-width),(image_no-1)*int(SQUARE_MEASUREMENTS/12)))#it draws it to the screen in the correct position


def write_instructions():#calculates how many characters can go on each line, where they are drawn to and then draws the text to the screen
    instructions = import_instructions()#gets the text from a JSON file
    letter_height = (INSTRUCTION_FONT.render("H", False, (0, 0, 0))).get_height() #calculates the height a letter will be using the font size selected
    start_pos = WINDOW_WIDTH * 13 / 320
    for instruction in instructions:#going through each instruction in the 11 instructions written for each screenshot
        instruction_list = render_instruction_text(font, instructions[instruction], COLOURS["BLACK"],WINDOW_WIDTH - (2 * WINDOW_WIDTH * 3 / 20))#seperates the instruction into a list each element contains the maximum amount of characters that can fit in the space given
        new_line = start_pos#gets the starting position for the instruction
        for line in instruction_list:#goes through the text elements in the instruction list and draws them to the screen
            render_text(win, INSTRUCTION_FONT, line, COLOURS["BLACK"], (WINDOW_WIDTH / 2, new_line))
            new_line += letter_height #before it draws the next series of text from the same instruction it adds the letter height so the next bit of text is just underneath
        start_pos += int(SQUARE_MEASUREMENTS / 12)#adds 1/12 of the height as the 11 images are evenly spread going down the window


def import_instructions():
    with open("instructions_writing.json") as f:
        file = json.load(f)
        f.close()
    return file


def calculate_picture_size(picture):#calculates the correct re-size of the image depending on it's actual height and width
    width = picture.get_width()
    height = picture.get_height()
    if -5 < width - height < 5:#if the width and height are similar then the image will be drawn square
        width = WINDOW_WIDTH*21/256
    elif width > height:
        width = WINDOW_WIDTH*3/20
    else:
        width = WINDOW_WIDTH*7/128
    height= WINDOW_WIDTH*21/256
    return int(width), int(height)


def start_options():#this is used before the main monopoly game begins to allow the user to join the game
    start_screen = True
    instructions = False
    while start_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_screen_buttons[0].check_for_press() and not instructions:
                    start_screen = False
                elif start_screen_buttons[1].check_for_press() and not instructions:
                    instructions = True
                elif start_screen_buttons[2].check_for_press() and instructions:
                    instructions = False
        draw_start_screen() if instructions is False else show_instructions()
        pygame.display.update()

def draw_wait_for_players():
    pygame.draw.rect(board, COLOURS["BOARD COLOUR"], (0, 0, SQUARE_MEASUREMENTS, SQUARE_MEASUREMENTS))
    pygame.draw.rect(board, COLOURS["BLACK"], (0, 0, SQUARE_MEASUREMENTS, SQUARE_MEASUREMENTS), 5)
    wait_for_players_buttons[0].draw(board)





def redraw_window(action_taken,pl_list, turn, other_card,deal, auction, game_finished):

    board.fill((200,200,255))

    board.draw_background(pl_list, turn)

    for i in pl_list:
        i.draw(board)

    if action_taken == 3 or action_taken == 4:
        deal.draw()

    elif action_taken == 6:
        auction.draw()

    board.draw_onto_board(pl_list[turn].pos, action_taken, other_card)

    if turn == -1:
        draw_wait_for_players()

    if game_finished:
        board.draw_end_screen(pl_list, turn)

    win.blit(board, (0, 0))


def main_game_loop():
    run = True
    recieved_board, action_taken, players, recieved_turn, other_card, deal, auction = server.send("info")
    turn, game_finished = recieved_turn
    while run:
        clock.tick(30)

        data = "info"

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:

                x = board.check_for_button_click(action_taken)#instead of checking button it could send mouse co-ords then server finds button
                if x is not None:
                    data = x
                else:
                    data = "mousepos" + " " + str(pygame.mouse.get_pos()[0]) + " " + str(pygame.mouse.get_pos()[1])
                if turn == -1:
                    if len(players) == 1:
                        print("Can not start with only one player")
                    elif wait_for_players_buttons[0].check_for_press() and list(players).index(current_id) ==0:
                        data = "START"
                if game_finished:
                    data = "info"
            if event.type == pygame.QUIT:
                sys.exit()




        try:
            recieved_board, action_taken, players, recieved_turn, other_card, recieved_deal, recieved_auction = server.send(data)

            turn = recieved_turn[0]
            game_finished = recieved_turn[1]


            pl_list = [] #need to make this a function where the info is turned into instances to actually be used
            k = 0
            for i in list(players):
                pl_list.append(Player(*players[i]))
                property_index = pl_list[k].owned_propertys
                pl_list[k].owned_propertys = []
                for ind in property_index:
                    pl_list[k].add_property(board.properties[ind], board)
                k += 1

            board.convert_for_use(recieved_board, pl_list)

            if recieved_auction is not None:
                auction = Auction(pl_list, recieved_auction[0], board)
                auction.amounts = recieved_auction[1]
                auction.amount = recieved_auction[2]
                auction.turn = recieved_auction[3]

            if recieved_deal is not None:
                deal = Deal(pl_list[turn],pl_list[recieved_deal[0]], board)
                deal.propertys_give = [board.properties[i] for i in recieved_deal[1]]
                deal.propertys_get = [board.properties[i] for i in recieved_deal[2]]
                deal.money_give = recieved_deal[3]
                deal.money_get = recieved_deal[4]

            redraw_window(action_taken, pl_list, turn, other_card, deal, auction, game_finished)
            pygame.display.update()
        except:
            print("ONE LOVE")
            print(traceback.format_exc())
            run = False


    server.disconnect()
    #pygame.quit()
    #quit()






"""while True:
    name = input("Please enter your name: ")
    if 0 < len(name) < 20:
        break
    else:
        print("Error, this name is not allowed (must be between 1 and 19 characters)")"""
name = "1"



pygame.display.set_caption("Monopoly")
win = pygame.display.set_mode((WINDOW_WIDTH, SQUARE_MEASUREMENTS))
while True:
    start_options()
    server = Network()
    current_id = server.connect(name)
    clock = pygame.time.Clock()
    board = Board(WINDOW_WIDTH, SQUARE_MEASUREMENTS)
    main_game_loop()
