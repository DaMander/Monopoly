from player import Player
from player import *
from constants import *
from game_rules import *
from network import Network
import time

"""as it is i it can only do it when the numbers go up in the dictionary instead it needs to through the dictionarys as they come"""

def redraw_window(action_taken,pl_list, turn, other_card,deal, auction):


    board.fill((200,200,255))

    board.draw_background(pl_list, turn)

    for i in pl_list:
        i.draw(board)

    if action_taken == 3 or action_taken == 4:
        deal.draw()


    elif action_taken == 6:
        auction.draw()

    board.draw_onto_board(pl_list[turn].pos, action_taken, other_card)

    win.blit(board, (0, 0))


board = Board(WINDOW_WIDTH, WINDOW_HEIGHT)




"""while True:
    name = input("Please enter your name: ")
    if 0 < len(name) < 20:
        break
    else:
        print("Error, this name is not allowed (must be between 1 and 19 characters)")"""
name = "Dan"


pygame.display.set_caption("Monopoly")
win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

server = Network()
current_id = server.connect(name)
recieved_board, action_taken, players, turn, other_card, deal, auction = server.send("info")

clock = pygame.time.Clock()
run = True
while run:
    clock.tick(30)
    player = players[current_id]

    data = "info"

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            x = board.check_for_button_click(action_taken)#instead of checking button it could send muose co-ords then server finds button
            if x!= None:
                data = x
            else:
                data = "mousepos" + " " + str(pygame.mouse.get_pos()[0]) + " " + str(pygame.mouse.get_pos()[1])
        if event.type == pygame.QUIT:
            run = False





    recieved_board, action_taken, players, turn, other_card, recieved_deal, recieved_auction = server.send(data)

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

    if recieved_auction != None:
        auction = Auction(pl_list, recieved_auction[0], board)
        auction.amounts = recieved_auction[1]
        auction.amount = recieved_auction[2]
        auction.turn = recieved_auction[3]

    if recieved_deal != None:
        deal = Deal(pl_list[turn],pl_list[recieved_deal[0]], board)
        deal.propertys_give = [board.properties[i] for i in recieved_deal[1]]
        deal.propertys_get = [board.properties[i] for i in recieved_deal[2]]

    redraw_window(action_taken, pl_list, turn, other_card, deal, auction)
    pygame.display.update()

server.disconnect()
pygame.quit()
quit()
