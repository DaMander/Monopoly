import json
import traceback

from player import *
from constants import *
from game_rules import *
from network import Network
from board import Button
import sys


def import_instructions():
    with open("instructions_writing.json") as f:
        file = json.load(f)
        f.close()
    return file


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


class Client:
    def __init__(self):
        self.action_taken = 0
        self.pl_list = []
        self.turn = 0
        self.other_card = None
        self.deal = None
        self.auction = None
        self.game_finished = False
        self.game_modes = {"Free Parking": False,
                           "No Sets": False,
                           "Land On GO Get 400": False}


        self.start_screen_buttons = [
            Button("START GAME", WINDOW_WIDTH / 4, 3 * SQUARE_MEASUREMENTS / 4, COLOURS["GREEN"], True, int(WINDOW_WIDTH / 5)),
            Button("INSTRUCTIONS", WINDOW_WIDTH/2, 3*SQUARE_MEASUREMENTS/4, COLOURS["BROWN"], True, int(WINDOW_WIDTH/5)),
            Button("BACK", WINDOW_WIDTH//2,WINDOW_WIDTH*1/64, COLOURS["RED"], True, BUTTON_WIDTH, WINDOW_WIDTH*1/32)]#as the board class is not initialised yet these buttons are only used to start the game


    def draw_start_screen(self):#draws the first screen you see when you start the client
        win.fill((200, 255, 200))
        render_text(win, title_font, "Monopoly", (255, 0, 0), (WINDOW_WIDTH / 2, SQUARE_MEASUREMENTS / 4))
        self.start_screen_buttons[0].draw(win)
        self.start_screen_buttons[1].draw(win)


    def show_instructions(self):#when player clicks instructions button this will draw the graphics to the screen
        pygame.draw.rect(win, (200, 255, 200), (0, 0, WINDOW_WIDTH, SQUARE_MEASUREMENTS))
        self.start_screen_buttons[2].draw(win)#draws BACK button
        self.draw_screenshots()
        write_instructions()


    def draw_screenshots(self):#draws screenshots of the game to explain the instructions
        for image_no in range(1, 12):#I called the images 1,2,3,4, etc. so I could use a for loop to acess them easier
            screenshot = pygame.image.load(f"Game_screenshots/{str(image_no)}.png")
            width, height = calculate_picture_size(screenshot)#calculates the picture size depending on how big the window width is
            screenshot = pygame.transform.scale(screenshot,(width,height))#the image is re-sized to what will fit on the screen
            win.blit(screenshot, (((image_no-1)%2)*(WINDOW_WIDTH-width),(image_no-1)*int(SQUARE_MEASUREMENTS/12)))#it draws it to the screen in the correct position

    def start_options(self):#this is used before the main monopoly game begins to allow the user to join the game
        start_screen = True
        instructions = False
        while start_screen:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_screen_buttons[0].check_for_press() and not instructions:
                        start_screen = False
                    elif self.start_screen_buttons[1].check_for_press() and not instructions:
                        instructions = True
                    elif self.start_screen_buttons[2].check_for_press() and instructions:
                        instructions = False
            self.draw_start_screen() if instructions is False else self.show_instructions()
            pygame.display.update()

    def draw_wait_for_players(self):
        pygame.draw.rect(board, COLOURS["BOARD COLOUR"], (0, 0, SQUARE_MEASUREMENTS, SQUARE_MEASUREMENTS))
        pygame.draw.rect(board, COLOURS["BLACK"], (0, 0, SQUARE_MEASUREMENTS, SQUARE_MEASUREMENTS), 5)
        for button in board.wait_for_players_buttons:
            button.draw(board)
            if button.text in self.game_modes.keys():
                if self.game_modes[button.text]:
                    button.color = COLOURS["GREEN"]
                else:
                    button.color = COLOURS["RED"]

    def convert_players(self, players):
        self.pl_list = []
        current_player = 0
        for i in list(players):
            self.pl_list.append(Player(*players[i]))
            property_index = self.pl_list[current_player].owned_propertys
            self.pl_list[current_player].owned_propertys = []
            for ind in property_index:
                self.pl_list[current_player].add_property(board.properties[ind], board)
            current_player += 1

    def convert_auction(self, recieved_auction):
        if recieved_auction is not None:
            self.auction = Auction(self.pl_list, recieved_auction[0], board)
            self.auction.amounts = recieved_auction[1]
            self.auction.amount = recieved_auction[2]
            self.auction.turn = recieved_auction[3]
        else:
            self.auction = None

    def convert_deal(self, recieved_deal):
        if recieved_deal is not None:
            self.deal = Deal(self.pl_list[self.turn], self.pl_list[recieved_deal[0]], board)
            self.deal.propertys_give = [board.properties[i] for i in recieved_deal[1]]
            self.deal.propertys_get = [board.properties[i] for i in recieved_deal[2]]
            self.deal.money_give = recieved_deal[3]
            self.deal.money_get = recieved_deal[4]
        else:
            self.deal = None

    def get_game_modes(self, game_modes):
        game_mode_number = 0
        for key, value in self.game_modes.items():
            self.game_modes[key] = game_modes[game_mode_number]
            game_mode_number += 1

    def decide_data_to_send(self, button_click):
        if button_click is not None:
            data = button_click
        else:
            data = "mousepos" + " " + str(pygame.mouse.get_pos()[0]) + " " + str(pygame.mouse.get_pos()[1])
        if self.turn == -1:
            for button in board.wait_for_players_buttons:
                if button.check_for_press():
                    data = button.text
        if self.game_finished:
            data = "info"
        return data

    def redraw_window(self):

        board.fill((200,200,255))

        board.draw_background(self.pl_list, self.turn)

        for player in self.pl_list:
            player.draw(board)

        if self.action_taken == 3 or self.action_taken == 4:
            self.deal.draw()

        elif self.action_taken == 6:
            self.auction.draw()

        board.draw_onto_board(self.pl_list[self.turn].pos, self.action_taken, self.other_card)

        if self.turn == -1:
            self.draw_wait_for_players()

        if self.game_finished:
            board.draw_end_screen(self.pl_list, self.turn)

        win.blit(board, (0, 0))


    def main_game_loop(self):
        run = True
        recieved_board, action_taken, players, recieved_turn, other_card, deal, auction, game_modes = server.send("info")
        self.turn, self.game_finished = recieved_turn
        while run:
            clock.tick(30)

            data = "info"

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    button_click = board.check_for_button_click(self.action_taken)#instead of checking button it could send mouse co-ords then server finds button
                    data = self.decide_data_to_send(button_click)

                if event.type == pygame.QUIT:
                    sys.exit()

            try:
                recieved_server_info = server.send(data)
                if len(recieved_server_info) == 7:
                    recieved_board, self.action_taken, players, recieved_turn, other_card, recieved_deal, recieved_auction = recieved_server_info
                else:
                    recieved_board, self.action_taken, players, recieved_turn, other_card, recieved_deal, recieved_auction, game_modes = recieved_server_info
                    self.get_game_modes(game_modes)

                self.turn = recieved_turn[0]
                self.game_finished = recieved_turn[1]
                self.other_card = other_card
                self.convert_players(players)
                self.convert_auction(recieved_auction)
                self.convert_deal(recieved_deal)
                board.convert_for_use(recieved_board, self.pl_list)

                self.redraw_window()
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
    client = Client()
    client.start_options()
    server = Network()
    current_id = server.connect(name)
    clock = pygame.time.Clock()
    board = Board(WINDOW_WIDTH, SQUARE_MEASUREMENTS)
    client.main_game_loop()